# brain-audit — measure a folder, verify its brAIn

> 🧠 [Hub](README.md) · [Variables](brain.yaml) · Methodology & results: [../Audit.md](../Audit.md)

A dependency-free auditor (Python ≥ 3.9, stdlib only). Given a folder it reports, as paste-ready Markdown:

1. **Token estimate** per file and per folder (chars ÷ 3.5 heuristic — see [../Audit.md](../Audit.md));
2. **Full-scan cost** (read everything) vs **hub-navigation cost** (hubs + `brain.yaml` on the path, then the target file) for every lookup scenario, with % savings;
3. **Link integrity**: broken relative Markdown links and orphan files unreachable from the root hub.

Per [rule 4](../brAIn.md), the code lives inside this file. Extract and run it from the repo root:

```bash
awk '/^```python$/{code=1; next} /^```$/{code=0} code' tools/brain-audit.md > brain_audit.py
python3 brain_audit.py examples/madame-martin/after
```

The script exits non-zero if it finds broken links or orphan files, so it can gate CI.

## The code

```python
#!/usr/bin/env python3
"""brain-audit: dependency-free auditor for brAIn folders (Python >= 3.9).

Usage: python3 brain_audit.py <folder>
Reports token costs, full-scan vs hub-navigation savings, and link integrity,
as paste-ready Markdown. Exits 1 on broken links or orphan files.
"""
import re
import sys
from pathlib import Path

CHARS_PER_TOKEN = 3.5   # rough chars-per-token heuristic for English/code
HUB = "README.md"       # rule 1: the folder hub
VARS = "brain.yaml"     # rule 6: the folder variables file
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(`{3,})")
CODE_SPAN_RE = re.compile(r"`[^`\n]+`")


def walk_files(root):
    """Every regular file under root, skipping hidden dirs/files (.git, .claude...)."""
    return [p for p in sorted(root.rglob("*"))
            if p.is_file()
            and not any(part.startswith(".") for part in p.relative_to(root).parts)]


def read(path):
    return path.read_text(encoding="utf-8", errors="replace")


def strip_fences(text):
    """Drop fenced code blocks: links inside code are examples, not navigation."""
    out, fence = [], 0
    for line in text.splitlines():
        m = FENCE_RE.match(line.strip())
        if m:
            n = len(m.group(1))
            fence = n if not fence else (0 if n >= fence else fence)
            continue
        if not fence:
            out.append(line)
    return "\n".join(out)


def md_links(path):
    """Relative link targets of a Markdown file (code and non-path refs excluded)."""
    text = CODE_SPAN_RE.sub("", strip_fences(read(path)))
    targets = []
    for raw in LINK_RE.findall(text):
        t = raw.split("#", 1)[0]
        if not t or "://" in raw or raw.startswith(("mailto:", "#")):
            continue
        if "." not in t and "/" not in t:
            continue  # bare reference id like [Claude](1), not a path
        targets.append(t)
    return targets


def broken_links(root, files):
    out = []
    for p in files:
        if p.suffix.lower() != ".md":
            continue
        for t in md_links(p):
            if not (p.parent / t).resolve().exists():
                out.append((p.relative_to(root), t))
    return out


def reachable_from_hub(root, files):
    """BFS over Markdown links starting at the root hub. None if there is no hub."""
    hub = root / HUB
    if not hub.is_file():
        return None
    seen, stack = set(), [hub.resolve()]
    while stack:
        p = stack.pop()
        if p in seen:
            continue
        seen.add(p)
        if p.suffix.lower() != ".md":
            continue
        for t in md_links(p):
            q = (p.parent / t).resolve()
            if q.is_dir():
                q = q / HUB  # a link to a folder counts as a link to its hub
            if q.is_file():
                stack.append(q)
    return seen


def nav_cost(root, target, toks):
    """Hub-navigation cost: every hub and brain.yaml on the path, then the target."""
    cost, cur = 0, root
    for part in (None,) + target.relative_to(root).parts[:-1]:
        cur = cur / part if part else cur
        for name in (HUB, VARS):
            f = cur / name
            if f in toks and f != target:
                cost += toks[f]
    return cost + toks[target]


def main():
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit("usage: python3 brain_audit.py <folder>")
    root = Path(sys.argv[1]).resolve()
    files = walk_files(root)
    toks = {p: round(len(read(p)) / CHARS_PER_TOKEN) for p in files}
    total = sum(toks.values())
    hub = root / HUB

    print(f"# brain-audit — `{root.name}`\n")

    print("## Tokens per file\n")
    print("| File | Chars | Tokens (est.) |")
    print("|---|---:|---:|")
    for p in files:
        print(f"| {p.relative_to(root)} | {len(read(p))} | {toks[p]} |")
    print(f"| **Total (full-scan cost)** |  | **{total}** |\n")

    folders = {}
    for p in files:
        d = str(p.relative_to(root).parent)
        folders[d] = folders.get(d, 0) + toks[p]
    if len(folders) > 1:
        print("## Tokens per folder\n")
        print("| Folder | Tokens (est.) |")
        print("|---|---:|")
        for d in sorted(folders):
            print(f"| {'(root)' if d == '.' else d + '/'} | {folders[d]} |")
        print()

    print("## Lookup cost: full scan vs hub navigation\n")
    if hub.is_file():
        print("| Scenario: read one file | Hub navigation | Full scan | Savings |")
        print("|---|---:|---:|---:|")
        for p in files:
            if p.name in (HUB, VARS):
                continue
            n = nav_cost(root, p, toks)
            print(f"| {p.relative_to(root)} | {n} | {total}"
                  f" | {100 * (total - n) / total:.1f}% |")
        print()
    else:
        print(f"No `{HUB}` hub at the root: an agent has no index and must "
              f"read everything — **{total} tokens** per lookup.\n")

    print("## Link integrity\n")
    broken = broken_links(root, files)
    for f, t in broken:
        print(f"- BROKEN: `{f}` -> `{t}`")
    print(f"Broken relative links: **{len(broken)}**\n")

    orphans = []
    seen = reachable_from_hub(root, files)
    if seen is None:
        print(f"Orphan files: *(skipped — no root `{HUB}`)*")
    else:
        orphans = [p.relative_to(root) for p in files if p.resolve() not in seen]
        for o in orphans:
            print(f"- ORPHAN: `{o}`")
        print(f"Orphan files (unreachable from the root hub): **{len(orphans)}**")

    sys.exit(1 if broken or orphans else 0)


if __name__ == "__main__":
    main()
```

## Notes

- The heuristic (`chars ÷ 3.5`) is deliberately model-agnostic; real tokenizers vary by ±15%, but before/after **ratios** are stable.
- Hidden folders (`.git/`, `.claude/`…) are excluded from the scan; link *targets* inside them are still checked for existence.
- Links inside code fences or inline code spans are treated as examples, and `[text](1)`-style numeric references are not paths — none of these counts as navigation.
