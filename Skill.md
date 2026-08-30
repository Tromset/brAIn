---
name: brainify
description: Transforms any folder or repository into a brAIn structure optimized for LLM navigation — README.md hubs, brain.yaml variables files, everything in Markdown, relative hyperlinks — to radically reduce token consumption per lookup. Use when the user says "brainify", "brAInify", mentions brAIn structure, hubs and brain.yaml files, or asks to reorganize a folder so AI agents can navigate it cheaply.
---
# Brainify — turn a folder into a brAIn
A brAIn is a folder where a small navigation layer (hubs + variables files) routes an agent straight to the one file it needs, instead of forcing a full scan. Apply the 6 rules below to the target folder, then verify with the auditor.
## The 6 rules
1. **Every folder has a hub** — a `README.md`: title + one-line purpose, navigation header (link to parent hub and to the folder's `brain.yaml`), a table of every content file with a one-liner, and links to each subfolder's `README.md`.
2. **Files are connected by hyperlinks** — every content file starts with a navigation header (blockquote linking to the hub, `brain.yaml`, and related siblings). All links are relative Markdown links. No broken links, no orphan files (everything reachable from the root hub).
3. **All content files are Markdown** — convert `.txt`, notes, exported docs to structured `.md`.
4. **Code lives inside Markdown code fences** with a language tag. One `.md` file can hold several fences (e.g. HTML + CSS of one page).
5. **MCPs and deep configs stay `.json`** — don't convert machine-consumed config; link it from the folder's hub so it isn't an orphan.
6. **Every folder has a `brain.yaml`** — a compact variables card with a `when_to_read` routing table (question → file). This is the key token-saving field.
### brain.yaml schema
```yaml
# brain.yaml — folder variables (brAIn rule 6)
name: <folder-name>
purpose: "<one line>"
parent: ../brain.yaml          # null at the project root
children: []                   # subfolders, each with its own README.md + brain.yaml
files:
  file.md: "<one-liner>"
when_to_read:                  # routing table: agent question -> file to open
  "<question>": file.md
links: {}                      # optional external references
```
All fields required except `links`.
## Transformation workflow
1. **Inventory** the target folder: list every file and subfolder, note formats and roles. Skip hidden directories (`.git/`, `.cursor/`, `node_modules/`...).
2. **Optionally split context from code** (recommended for projects mixing docs and source): create `Agents/` (context, objectives, constraints, decisions, tasks) and `Code/` (real source files agents modify), and sort existing files by role without losing information.
3. **Convert** non-Markdown content files to `.md` (rule 3), embedding code in language-tagged fences (rule 4). Keep deep configs as `.json` (rule 5). Preserve all information.
4. **Create per folder** a `README.md` hub (rule 1) and a `brain.yaml` (rule 6) using the templates in [templates.md](templates.md). Write a meaningful `when_to_read` for each folder.
5. **Wire links** (rule 2): navigation header at the top of every content file, hub tables listing every file, parent/child hub links.
6. **Verify** with the auditor (see below). Fix any broken link or orphan file it reports and re-run until it exits 0.
## Verification
Run the bundled dependency-free auditor (Python ≥ 3.9, stdlib only):
```bash
python3 scripts/brain_audit.py <target-folder>
```
It reports token estimates, full-scan vs hub-navigation savings per file, broken relative links, and orphan files. A valid brAIn requires **0 broken links and 0 orphan files** (non-zero exit otherwise). Include the savings table in your summary to the user.
## Additional resources
- Ready-to-copy file templates (hub, `brain.yaml`, content file, config): [templates.md](templates.md)
- Full specification and worked before/after example: the brAIn repo, if present in the workspace (`brAIn.md`, `examples/`)
# templates.md — Ready-to-copy brAIn files
The four files a brAInified folder needs. Copy a fence into the target file, replace every `<placeholder>`, delete what doesn't apply.
## 1. The hub — `README.md` (rule 1)
````markdown
# <folder-name> — <one-line purpose>
> 🧠 [Parent hub](../README.md) · [Variables](brain.yaml)
<Two or three sentences: what this folder contains and when an agent should come here.>
## Files
| File | What it contains |
|---|---|
| [file.md](file.md) | <one-liner> |
| [config.json](config.json) | <one-liner — deep config, stays JSON (rule 5)> |
## Subfolders
- [<subfolder>/](<subfolder>/README.md) — <one-liner>
````
## 2. The variables file — `brain.yaml` (rule 6)
```yaml
# brain.yaml — folder variables (brAIn rule 6)
name: <folder-name>
purpose: "<one line>"
parent: ../brain.yaml          # null at the project root
children: []                   # e.g. [assets/, docs/] — each gets its own README.md + brain.yaml
files:
  file.md: "<one-liner>"
  config.json: "<one-liner — deep config, stays JSON>"
when_to_read:                  # routing table: question an agent might have -> file to open
  "<question>": file.md
links: {}                      # optional external references (URLs, tickets, dashboards)
```
## 3. A content file — `<name>.md` (rules 2–4)
````markdown
# <file title>
> 🧠 [Hub](README.md) · [Variables](brain.yaml)
<What this file contains, in one or two sentences. Link related sibling files
inline, e.g. "see the config in [config.json](config.json)".>
## <section>
Code lives inside the Markdown file, in a fenced block tagged with its
language (rule 4). One file can hold several fences (e.g. the HTML and the
CSS of one page).
````
## 4. A deep config — `config.json` (rule 5)
MCPs and machine-consumed configs stay `.json`; link them from the folder's hub so they are not orphans.
```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "<command>",
      "args": []
    }
  }
}
```