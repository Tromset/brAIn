#!/usr/bin/env python3
"""brainify — turn any folder into a brAIn (stdlib only, Python ≥ 3.9).

Usage:
  python3 scripts/brainify.py <folder> [--no-split] [--force] [--dry-run] [--no-audit]

Applies the 6 brAIn rules with a styled multi-stage progress UI, then runs
the bundled auditor unless --no-audit is set.

Layout rules: every folder that directly holds content files gets Agents/ +
Code/ (folders holding only subfolders stay pure navigation nodes). Code/
receives real code files only and never gets generated files (no hub, no
brain.yaml, no conversions) — Markdown, docs, and configs go to Agents/.
Code/ files are linked from the parent folder's hub instead.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HUB = "README.md"
VARS = "brain.yaml"
SKIP_DIR_NAMES = {
    ".git", ".hg", ".svn", ".cursor", ".claude", ".vscode",
    "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".tox", ".mypy_cache", ".pytest_cache", "coverage",
}
KEEP_AS_IS = {".json", ".yaml", ".yml"}  # deep configs / already yaml
CONVERT_TO_MD = {".txt", ".text", ".rst", ".mdown", ".markdown"}
CODE_LANG = {
    ".html": "html", ".htm": "html", ".css": "css", ".scss": "scss",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "tsx", ".jsx": "jsx",
    ".py": "python", ".rb": "ruby", ".go": "go", ".rs": "rust",
    ".java": "java", ".kt": "kotlin", ".swift": "swift",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash",
    ".sql": "sql", ".r": "r", ".php": "php",
    ".toml": "toml", ".ini": "ini", ".env": "bash",
}
# Config-like extensions map to a fence language for conversion but are not
# "real code" for the Agents/Code split — they belong with the context.
CONFIG_EXTS = {".toml", ".ini", ".env"}
SPLIT_EXCLUDE = {"Agents", "Code"}  # never re-split inside these subtrees
NAV_RE = re.compile(r"^>\s*🧠")
STEPS = [
    ("inventory", "Inventory"),
    ("split", "Split Agents / Code"),
    ("convert", "Convert to Markdown"),
    ("hubs", "Write hubs"),
    ("vars", "Write brain.yaml"),
    ("wire", "Wire hyperlinks"),
    ("audit", "Verify integrity"),
]

# ---------------------------------------------------------------------------
# Styled progress UI (ANSI, no deps)
# ---------------------------------------------------------------------------

class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    BLUE = "\033[34m"
    WHITE = "\033[97m"
    BG_DIM = "\033[48;5;236m"

    @classmethod
    def enabled(cls) -> bool:
        return sys.stdout.isatty() and not os.environ.get("NO_COLOR")

    @classmethod
    def c(cls, code: str, text: str) -> str:
        if not cls.enabled():
            return text
        return f"{code}{text}{cls.RESET}"


def _bar(frac: float, width: int = 28) -> str:
    frac = max(0.0, min(1.0, frac))
    filled = int(round(frac * width))
    empty = width - filled
    if Style.enabled():
        body = (
            Style.c(Style.CYAN + Style.BOLD, "█" * filled)
            + Style.c(Style.DIM, "░" * empty)
        )
        return f"[{body}]"
    return f"[{'#' * filled}{'-' * empty}]"


def _pct(frac: float) -> str:
    return f"{int(round(frac * 100)):3d}%"


class Progress:
    """Multi-stage pipeline progress with a live bar + checklist."""

    def __init__(self, title: str, steps: list[tuple[str, str]]):
        self.title = title
        self.steps = steps
        self.status: dict[str, str] = {k: "pending" for k, _ in steps}
        self.current: str | None = None
        self.detail = ""
        self.sub_frac = 0.0
        self._drawn = 0
        self._started = time.monotonic()

    def _overall(self) -> float:
        weights = {"pending": 0.0, "active": 0.5, "done": 1.0, "skip": 1.0, "fail": 1.0}
        total = sum(weights[self.status[k]] for k, _ in self.steps)
        # refine active step with sub-progress
        if self.current and self.status.get(self.current) == "active":
            total = total - 0.5 + 0.5 * self.sub_frac
        return total / max(len(self.steps), 1)

    def _icon(self, state: str) -> str:
        icons = {
            "pending": Style.c(Style.DIM, "·"),
            "active": Style.c(Style.YELLOW + Style.BOLD, "▸"),
            "done": Style.c(Style.GREEN + Style.BOLD, "✓"),
            "skip": Style.c(Style.DIM, "–"),
            "fail": Style.c(Style.RED + Style.BOLD, "✗"),
        }
        return icons.get(state, "?")

    def render(self, *, force: bool = False) -> None:
        # Outside a TTY, only redraw on meaningful transitions (not every tick).
        if not Style.enabled() and not force and self.status.get(self.current) == "active":
            if self.sub_frac not in (0.0, 1.0) and self.sub_frac < 0.999:
                return

        lines: list[str] = []
        elapsed = time.monotonic() - self._started
        frac = self._overall()
        header = (
            f"  {Style.c(Style.MAGENTA + Style.BOLD, '🧠  brAInify')}"
            f"  {Style.c(Style.DIM, '·')}  {Style.c(Style.WHITE + Style.BOLD, self.title)}"
        )
        lines.append("")
        lines.append(header)
        lines.append(
            f"  {_bar(frac)}  {Style.c(Style.CYAN + Style.BOLD, _pct(frac))}"
            f"  {Style.c(Style.DIM, f'{elapsed:5.1f}s')}"
        )
        lines.append("")
        for key, label in self.steps:
            state = self.status[key]
            mark = self._icon(state)
            name = Style.c(Style.BOLD, label) if state == "active" else label
            if state == "done":
                name = Style.c(Style.GREEN, label)
            elif state == "fail":
                name = Style.c(Style.RED, label)
            elif state == "pending":
                name = Style.c(Style.DIM, label)
            extra = ""
            if key == self.current and self.detail:
                extra = f"  {Style.c(Style.DIM, self.detail)}"
                if state == "active" and self.sub_frac:
                    extra += f"  {_bar(self.sub_frac, 12)} {Style.c(Style.DIM, _pct(self.sub_frac))}"
            lines.append(f"  {mark}  {name}{extra}")
        lines.append("")

        if Style.enabled() and self._drawn:
            sys.stdout.write(f"\033[{self._drawn}A")
            for line in lines:
                sys.stdout.write(f"\033[2K{line}\n")
        else:
            sys.stdout.write("\n".join(lines) + "\n")
        self._drawn = len(lines)
        sys.stdout.flush()

    def start(self, key: str, detail: str = "") -> None:
        self.current = key
        self.status[key] = "active"
        self.detail = detail
        self.sub_frac = 0.0
        self.render(force=True)

    def tick(self, detail: str = "", frac: float | None = None) -> None:
        if detail:
            self.detail = detail
        if frac is not None:
            self.sub_frac = frac
        self.render()
        if Style.enabled():
            time.sleep(0.015)

    def done(self, detail: str = "") -> None:
        if self.current:
            self.status[self.current] = "done"
            self.detail = detail
            self.sub_frac = 1.0
            self.render(force=True)

    def skip(self, key: str, detail: str = "") -> None:
        self.status[key] = "skip"
        self.current = key
        self.detail = detail
        self.sub_frac = 1.0
        self.render(force=True)

    def fail(self, detail: str = "") -> None:
        if self.current:
            self.status[self.current] = "fail"
            self.detail = detail
            self.render(force=True)

    def finish(self, ok: bool) -> None:
        if Style.enabled() and self._drawn:
            sys.stdout.write("\n")
        elapsed = time.monotonic() - self._started
        if ok:
            print(
                f"  {Style.c(Style.GREEN + Style.BOLD, '✦  Done')}"
                f"  {Style.c(Style.DIM, f'— brAIn ready in {elapsed:.1f}s')}\n"
            )
        else:
            print(
                f"  {Style.c(Style.RED + Style.BOLD, '✦  Finished with issues')}"
                f"  {Style.c(Style.DIM, f'— {elapsed:.1f}s')}\n"
            )


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------

def is_skipped(path: Path, root: Path) -> bool:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return any(p in SKIP_DIR_NAMES or p.startswith(".") for p in parts)


def under_code(path: Path, root: Path) -> bool:
    """True if path lives inside (or is) a Code/ subtree — a no-write zone."""
    try:
        return "Code" in path.relative_to(root).parts
    except ValueError:
        return False


def is_code_file(path: Path) -> bool:
    ext = path.suffix.lower()
    return ext in CODE_LANG and ext not in CONFIG_EXTS


def iter_dirs(root: Path) -> list[Path]:
    dirs = [root]
    for p in sorted(root.rglob("*")):
        if p.is_dir() and not is_skipped(p, root):
            dirs.append(p)
    return dirs


def iter_files(root: Path) -> list[Path]:
    return [
        p for p in sorted(root.rglob("*"))
        if p.is_file() and not is_skipped(p, root)
    ]


def one_liner(name: str) -> str:
    stem = Path(name).stem.replace("-", " ").replace("_", " ").strip()
    if not stem:
        return name
    return stem[0].upper() + stem[1:] if len(stem) > 1 else stem.upper()


def yaml_escape(s: str) -> str:
    if any(c in s for c in ':#{}[]&*!|>\'"%@`') or s != s.strip():
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return f'"{s}"'


def has_nav_header(text: str) -> bool:
    for line in text.splitlines()[:8]:
        if NAV_RE.match(line.strip()):
            return True
    return False


# ---------------------------------------------------------------------------
# Transform pipeline
# ---------------------------------------------------------------------------

@dataclass
class Inventory:
    root: Path
    dirs: list[Path] = field(default_factory=list)
    files: list[Path] = field(default_factory=list)
    to_convert: list[Path] = field(default_factory=list)
    code_files: list[Path] = field(default_factory=list)
    keep_files: list[Path] = field(default_factory=list)


def inventory(root: Path) -> Inventory:
    inv = Inventory(root=root, dirs=iter_dirs(root), files=iter_files(root))
    for f in inv.files:
        if f.name in (HUB, VARS):
            continue
        if under_code(f, root):
            # Code/ subtrees are untouched: no conversion, no new files.
            inv.keep_files.append(f)
            continue
        ext = f.suffix.lower()
        if ext in CONVERT_TO_MD or (ext == "" and f.stat().st_size < 200_000):
            # bare text-ish files without extension also convert if small
            if ext in CONVERT_TO_MD:
                inv.to_convert.append(f)
            elif ext == "" and _looks_text(f):
                inv.to_convert.append(f)
        elif ext in CODE_LANG:
            inv.code_files.append(f)
        elif ext in KEEP_AS_IS or f.name.endswith(".json"):
            inv.keep_files.append(f)
        elif ext == ".md":
            inv.keep_files.append(f)
        else:
            # binary / unknown — leave alone, still link from hub if present
            inv.keep_files.append(f)
    return inv


def _looks_text(path: Path) -> bool:
    try:
        raw = path.read_bytes()[:2048]
    except OSError:
        return False
    if b"\x00" in raw:
        return False
    try:
        raw.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False


def convert_file(path: Path, dry: bool) -> Path:
    """Convert a text-like file into .md (possibly wrapping code). Returns new path."""
    text = path.read_text(encoding="utf-8", errors="replace")
    ext = path.suffix.lower()
    title = one_liner(path.name)
    if ext in CONVERT_TO_MD or ext == "":
        body = text if text.endswith("\n") else text + "\n"
        md = f"# {title}\n\n{body}"
    else:
        lang = CODE_LANG.get(ext, "")
        md = (
            f"# {title}\n\n"
            f"Source formerly at `{path.name}`.\n\n"
            f"```{lang}\n{text.rstrip()}\n```\n"
        )
    dest = path.with_suffix(".md")
    if dest == path:
        dest = path.parent / f"{path.name}.md"
    if not dry:
        dest.write_text(md, encoding="utf-8")
        if dest != path:
            path.unlink()
    return dest


def content_files_in(folder: Path, root: Path) -> list[Path]:
    """Non-hub, non-yaml files directly in folder."""
    out = []
    for p in sorted(folder.iterdir()):
        if not p.is_file():
            continue
        if is_skipped(p, root):
            continue
        if p.name in (HUB, VARS):
            continue
        out.append(p)
    return out


def child_dirs(folder: Path, root: Path) -> list[Path]:
    return [
        p for p in sorted(folder.iterdir())
        if p.is_dir() and not is_skipped(p, root)
    ]


def code_subtree_files(folder: Path, root: Path) -> list[Path]:
    """All files under folder/Code/, recursively. Code/ has no hub of its own,
    so these are listed directly in the parent folder's hub."""
    code = folder / "Code"
    if not code.is_dir():
        return []
    return [
        p for p in sorted(code.rglob("*"))
        if p.is_file() and not is_skipped(p, root)
    ]


def write_hub(folder: Path, root: Path, dry: bool, force: bool) -> None:
    hub_path = folder / HUB
    if hub_path.exists() and not force:
        # still ensure it will be linked; skip overwrite
        return
    name = folder.name if folder != root else root.name
    is_root = folder == root
    parent_link = "" if is_root else f"[Parent hub](../{HUB}) · "
    files = content_files_in(folder, root)
    kids = child_dirs(folder, root)
    # Code/ never gets its own hub — its files are listed here instead.
    nav_kids = [k for k in kids if k.name != "Code"]
    code_files = code_subtree_files(folder, root)

    rows = []
    for f in files:
        rows.append(f"| [{f.name}]({f.name}) | {one_liner(f.name)} |")
    for f in code_files:
        rel = f.relative_to(folder).as_posix()
        rows.append(f"| [{rel}]({rel}) | Code — {one_liner(f.name)} |")
    files_section = (
        "| File | What it contains |\n|---|---|\n" + "\n".join(rows)
        if rows else "_No content files at this level._"
    )

    sub_lines = [
        f"- [{k.name}/]({k.name}/{HUB}) — {one_liner(k.name)}"
        for k in nav_kids
    ]
    subs_section = "\n".join(sub_lines) if sub_lines else "_None._"

    purpose = (
        f"brAIn hub for `{name}` — entry point for agents navigating this folder."
    )
    body = f"""# {name} — {purpose}

> 🧠 {parent_link}[Variables]({VARS})

This folder is part of a brAIn structure. Start here, then open `{VARS}` to
route to the single file you need.

## Files

{files_section}

## Subfolders

{subs_section}
"""
    if not dry:
        hub_path.write_text(body, encoding="utf-8")


def write_brain_yaml(folder: Path, root: Path, dry: bool, force: bool) -> None:
    path = folder / VARS
    if path.exists() and not force:
        return
    name = folder.name if folder != root else root.name
    is_root = folder == root
    files = content_files_in(folder, root)
    kids = child_dirs(folder, root)
    nav_kids = [k for k in kids if k.name != "Code"]
    code_files = code_subtree_files(folder, root)

    children = ", ".join(f"{k.name}/" for k in nav_kids)
    children_line = f"[{children}]" if children else "[]"

    file_lines = [f"  {f.name}: {yaml_escape(one_liner(f.name))}" for f in files]
    file_lines += [
        f"  {f.relative_to(folder).as_posix()}: {yaml_escape('Code — ' + one_liner(f.name))}"
        for f in code_files
    ]
    files_block = "\n".join(file_lines) if file_lines else "  {}"

    wtr_lines = []
    for f in files:
        q = f"About {one_liner(f.name).lower()}?"
        wtr_lines.append(f"  {yaml_escape(q)}: {f.name}")
    for f in code_files:
        q = f"Edit {f.name}?"
        wtr_lines.append(f"  {yaml_escape(q)}: {f.relative_to(folder).as_posix()}")
    for k in nav_kids:
        q = f"Browse {k.name}/?"
        wtr_lines.append(f"  {yaml_escape(q)}: {k.name}/{HUB}")
    if not wtr_lines:
        wtr_lines.append(f'  "What is this folder?": {HUB}')
    wtr_block = "\n".join(wtr_lines)

    parent = "null" if is_root else f"../{VARS}"
    body = f"""# brain.yaml — folder variables (brAIn rule 6)
name: {name}
purpose: {yaml_escape(f"Variables and routing for {name}")}
parent: {parent}
children: {children_line}
files:
{files_block}
when_to_read:
{wtr_block}
links: {{}}
"""
    if not dry:
        path.write_text(body, encoding="utf-8")


def ensure_nav_header(path: Path, dry: bool) -> bool:
    """Prepend a nav header to a Markdown content file if missing. Returns True if changed."""
    if path.name == HUB or path.suffix.lower() != ".md":
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    if has_nav_header(text):
        return False
    header = f"> 🧠 [Hub]({HUB}) · [Variables]({VARS})\n\n"
    # insert after a leading # title if present
    lines = text.splitlines(keepends=True)
    if lines and lines[0].lstrip().startswith("#"):
        new = [lines[0], "\n", header] + lines[1:]
    else:
        new = [header] + lines
    if not dry:
        path.write_text("".join(new), encoding="utf-8")
    return True


def split_all(root: Path, dry: bool, progress: Progress) -> tuple[int, int]:
    """Create Agents/ + Code/ in every folder that directly holds content files.

    Folders holding only subfolders are left as pure navigation nodes, and the
    Agents/ and Code/ subtrees themselves are never re-split. Code/ receives
    only real code files — Markdown (even with embedded code), docs, and
    configs go to Agents/. Folders that already have Agents/ or Code/ are
    respected and skipped.
    """
    targets = []
    for d in iter_dirs(root):
        rel_parts = d.relative_to(root).parts
        if any(part in SPLIT_EXCLUDE for part in rel_parts):
            continue
        if (d / "Agents").is_dir() or (d / "Code").is_dir():
            continue
        files = content_files_in(d, root)
        if files:
            targets.append((d, files))

    total = sum(len(fs) for _, fs in targets)
    moved = 0
    for d, files in targets:
        agents, code = d / "Agents", d / "Code"
        if not dry:
            agents.mkdir(exist_ok=True)
            code.mkdir(exist_ok=True)
        for f in files:
            dest_dir = code if is_code_file(f) else agents
            moved += 1
            progress.tick(
                f"{f.name} → {dest_dir.relative_to(root)}/",
                moved / max(total, 1),
            )
            if not dry:
                shutil.move(str(f), str(dest_dir / f.name))
    return len(targets), moved


def run_audit(root: Path, progress: Progress) -> tuple[int, str]:
    audit = Path(__file__).resolve().parent / "brain_audit.py"
    if not audit.is_file():
        progress.fail("brain_audit.py missing")
        return 1, ""
    import subprocess
    progress.tick("running auditor…", 0.3)
    proc = subprocess.run(
        [sys.executable, str(audit), str(root)],
        capture_output=True,
        text=True,
    )
    progress.tick("auditor finished", 1.0)
    return proc.returncode, proc.stdout.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def brainify(root: Path, *, split: bool, force: bool, dry: bool, no_audit: bool) -> int:
    root = root.resolve()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    progress = Progress(str(root), STEPS)

    # 1. Inventory
    progress.start("inventory", "scanning…")
    inv = inventory(root)
    progress.tick(
        f"{len(inv.dirs)} dirs · {len(inv.files)} files",
        1.0,
    )
    progress.done(f"{len(inv.dirs)} dirs · {len(inv.files)} files")

    # 2. Split — Agents/ + Code/ in every folder that directly holds files
    if split:
        progress.start("split", "Agents/ + Code/…")
        n_folders, n_moved = split_all(root, dry, progress)
        progress.done(f"{n_folders} folders · {n_moved} files sorted")
        inv = inventory(root)  # refresh after moves
    else:
        progress.skip("split", "--no-split")

    # 3. Convert
    progress.start("convert", "converting…")
    converted = 0
    targets = list(inv.to_convert)
    # also wrap code into .md only when --embed-code; default keeps Code/ sources
    # (matches examples/after). Conversion covers .txt → .md.
    for i, f in enumerate(targets):
        progress.tick(f.name, (i + 1) / max(len(targets), 1))
        convert_file(f, dry)
        converted += 1
    progress.done(f"{converted} converted")

    # refresh after conversions; Code/ subtrees get no hub and no brain.yaml
    dirs = [d for d in iter_dirs(root) if not under_code(d, root)]

    # 4. Hubs
    progress.start("hubs", "writing README.md…")
    for i, d in enumerate(dirs):
        progress.tick(str(d.relative_to(root) or "."), (i + 1) / max(len(dirs), 1))
        write_hub(d, root, dry, force)
    progress.done(f"{len(dirs)} hubs")

    # 5. brain.yaml
    progress.start("vars", "writing brain.yaml…")
    for i, d in enumerate(dirs):
        progress.tick(str(d.relative_to(root) or "."), (i + 1) / max(len(dirs), 1))
        write_brain_yaml(d, root, dry, force)
    progress.done(f"{len(dirs)} yaml")

    # 6. Wire links (nav headers on content .md — never inside Code/)
    progress.start("wire", "nav headers…")
    md_files = [
        p for p in iter_files(root)
        if p.suffix.lower() == ".md" and p.name != HUB
        and not under_code(p, root)
    ]
    wired = 0
    for i, p in enumerate(md_files):
        progress.tick(p.name, (i + 1) / max(len(md_files), 1))
        if ensure_nav_header(p, dry):
            wired += 1
    # hubs already link files + children; yaml links via when_to_read
    # ensure root hub also links brain.yaml (already does) — done
    progress.done(f"{wired} headers added")

    # 7. Audit
    report = ""
    code = 0
    if no_audit or dry:
        progress.skip("audit", "skipped" + (" (dry-run)" if dry else ""))
    else:
        progress.start("audit", "verifying…")
        code, report = run_audit(root, progress)
        if code == 0:
            progress.done("0 broken · 0 orphans")
        else:
            progress.fail("integrity issues — see report")

    progress.finish(ok=(code == 0))

    if report:
        print(Style.c(Style.DIM, "─" * 60))
        print(report)
        print(Style.c(Style.DIM, "─" * 60))
        print()

    if dry:
        print(Style.c(Style.YELLOW, "  dry-run: no files were written.\n"))

    return code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="brainify",
        description="Turn any folder into a brAIn — hubs, brain.yaml, links, with styled progress.",
    )
    p.add_argument("folder", type=Path, help="Target folder to brAInify")
    p.add_argument(
        "--no-split",
        dest="split",
        action="store_false",
        help="Keep the existing layout (no Agents/ + Code/ folders)",
    )
    # Kept for compatibility: the split is now the default behavior.
    p.add_argument("--split", dest="split", action="store_true", help=argparse.SUPPRESS)
    p.set_defaults(split=True)
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing README.md / brain.yaml hubs",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show progress without writing files",
    )
    p.add_argument(
        "--no-audit",
        action="store_true",
        help="Skip the integrity auditor at the end",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return brainify(
            args.folder,
            split=args.split,
            force=args.force,
            dry=args.dry_run,
            no_audit=args.no_audit,
        )
    except KeyboardInterrupt:
        print("\n  aborted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
