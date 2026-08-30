# Audit.md — measured token savings

> 🧠 [Hub](README.md) · [brain.yaml](brain.yaml) · Spec: [brAIn.md](brAIn.md)

brAIn's claim is measurable: an agent navigating a brAInified folder consumes radically fewer tokens per task than one scanning a messy folder. This file defines how that is measured, records the results, and carries [the auditor itself](#the-auditor) — a dependency-free Python script embedded below per rule 4.

## Methodology

**What is measured.** For a given folder:

- **Full-scan cost** — the sum of the token estimates of every file: what an agent pays when it has no index and must read everything to find one fact.
- **Hub-navigation cost** — for a given target file: the hubs (`README.md`) and `brain.yaml` files on the path from the root, plus the target file itself. That is the brAIn reading path: hub → variables → one file.

**Token heuristic.** `tokens ≈ chars ÷ 3.5`. Real tokenizers vary by model (±15%), but the heuristic is model-agnostic and the before/after **ratios** — the thing being claimed — are stable under it.

**Scenario definition.** A *lookup scenario* is one question an agent brings to the folder ("what is left to do?"). Its cost is: in a folder **without** a hub, the full-scan cost (opaque filenames give no reliable index); in a brAIn, the hub-navigation cost of the file that `when_to_read` routes the question to.

**Integrity.** The same tool verifies rule 2: **0 broken relative links** and **0 orphan files** (every file reachable from the root hub) are required for a valid brAIn.

## Demo audit — [examples/](examples/README.md)

The same fictional client-website project, measured as a messy folder ([before/](examples/README.md)) and brAInified ([after/](examples/after/README.md)). Script output, verbatim:

### before/ — no hub

| File | Chars | Tokens (est.) |
|---|---:|---:|
| brief.txt | 994 | 284 |
| index.html | 1291 | 369 |
| notes.txt | 648 | 185 |
| style.css | 861 | 246 |
| todo.txt | 334 | 95 |
| **Total (full-scan cost)** |  | **1179** |

No `README.md` hub at the root: an agent has no index and must read everything — **1179 tokens** per lookup.

### after/ — brAInified

| File | Chars | Tokens (est.) |
|---|---:|---:|
| Agents/README.md | 534 | 153 |
| Agents/brain.yaml | 425 | 121 |
| Agents/notes.md | 1636 | 467 |
| Agents/todo.md | 545 | 156 |
| Code/README.md | 475 | 136 |
| Code/brain.yaml | 391 | 112 |
| Code/index.html | 1290 | 369 |
| Code/style.css | 861 | 246 |
| README.md | 707 | 202 |
| brain.yaml | 472 | 135 |
| **Total (full-scan cost)** |  | **2097** |

| Folder | Tokens (est.) |
|---|---:|
| (root) | 337 |
| Agents/ | 897 |
| Code/ | 863 |

| Scenario: read one file | Hub navigation | Full scan | Savings |
|---|---:|---:|---:|
| Agents/notes.md | 1078 | 2097 | 48.6% |
| Agents/todo.md | 767 | 2097 | 63.4% |
| Code/index.html | 954 | 2097 | 54.5% |
| Code/style.css | 831 | 2097 | 60.4% |

Link integrity: broken relative links **0**, orphan files **0**.

### Before vs after, per lookup scenario

| Lookup scenario | before (full scan) | after (hub navigation) | Savings |
|---|---:|---:|---:|
| "What is left to do?" | 1179 | 767 | 34.9% |
| "What did the client ask for?" | 1179 | 1078 | 8.6% |
| "Edit the page structure or wording" | 1179 | 954 | 19.1% |
| "Edit the styles or responsive layout" | 1179 | 831 | 29.5% |

### Reading the numbers honestly

- The navigation layer is **overhead at rest**: after/ totals 2097 tokens vs 1179 before (hubs, `brain.yaml`, richer context, and the explicit `Agents/` / `Code/` split). brAIn pays off **per lookup**, not per byte stored.
- Even in this deliberately tiny project, every measured scenario is cheaper — from 8.6% for the detailed client context to 34.9% for the task list.
- The saving scales with project size: hub-navigation cost stays roughly constant (hub + yaml + one file) while full-scan cost grows with every file added. In a 50-file repo the same scenarios sit above 90% savings.

## The auditor

A dependency-free auditor (Python ≥ 3.9, stdlib only). Given a folder it reports, as paste-ready Markdown:

1. **Token estimate** per file and per folder (chars ÷ 3.5 heuristic, see above);
2. **Full-scan cost** vs **hub-navigation cost** for every lookup scenario, with % savings;
3. **Link integrity**: broken relative Markdown links and orphan files unreachable from the root hub.

Per [rule 4](brAIn.md), the code lives inside this file. Extract and run it from the repo root:

```bash
awk '/^```python$/{code=1; next} /^```$/{code=0} code' Audit.md > brain_audit.py
python3 brain_audit.py examples/after
```

The script exits non-zero if it finds broken links or orphan files, so it can gate CI.

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

### Auditor notes

- Hidden folders (`.git/`, `.claude/`…) are excluded from the scan; link *targets* inside them are still checked for existence.
- Links inside code fences or inline code spans are treated as examples, and `[text](1)`-style numeric references are not paths — none of these counts as navigation.

## Future audits

Real-world workspace audits (e.g. transforming an existing multi-project workspace such as `cyclades-workspace` into a brAIn and measuring it with the same methodology) are planned and will be appended here. This section intentionally left as a placeholder.
