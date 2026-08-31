# scripts — brAInify CLI

> 🧠 [Parent hub](../README.md) · [Variables](brain.yaml)

Command-line tools to **brAInify any folder** and verify the result. Pure Python ≥ 3.9, stdlib only — styled progress bars, no dependencies to install.

## Quickstart

```bash
# From the repo root — pick a folder in Finder, then brAInify it
./brainify

# Or target a folder directly (with progress UI)
python3 scripts/brainify.py /path/to/folder

# Keep the existing layout (skip the Agents/ + Code/ split)
python3 scripts/brainify.py /path/to/folder --no-split

# Preview without writing
python3 scripts/brainify.py /path/to/folder --dry-run

# Audit only
python3 scripts/brain_audit.py /path/to/folder
```

Optional convenience symlink (no sudo — `~/.local/bin` is on PATH):

```bash
ln -sf "$(pwd)/brainify" ~/.local/bin/brainify   # run from the repo root
brainify                                         # Finder picker, from anywhere
brainify ~/my-project --split
```

## Files

| File | What it contains |
|---|---|
| [brainify.py](brainify.py) | Main CLI — inventory → convert → hubs → yaml → wire → audit, with styled bars |
| [brain_audit.py](brain_audit.py) | Integrity auditor — tokens, savings, broken links, orphans |

## What `brainify` does

1. **Inventory** — walk the tree (skips `.git/`, `node_modules/`, …)
2. **Split** — `Agents/` + `Code/` in every folder that directly holds files
   (folders holding only subfolders stay pure navigation nodes)
3. **Convert** — `.txt` (and similar) → structured `.md`, inside `Agents/`
4. **Hubs** — write a `README.md` in every folder — except `Code/`
5. **Variables** — write a `brain.yaml` with `when_to_read` routing — except `Code/`
6. **Wire** — add `> 🧠` navigation headers on content Markdown files
7. **Audit** — run [brain_audit.py](brain_audit.py) (0 broken links, 0 orphans)

The `Code/` rule: it holds **real code files only** and never receives
generated or converted files — no hub, no `brain.yaml`, no `.md`. Markdown
(even with embedded code), docs, and configs go to `Agents/`; the parent
folder's hub links each `Code/` file directly.

Flags: `--no-split` · `--force` · `--dry-run` · `--no-audit`.
