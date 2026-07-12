# brAIn — The Technology

> 🧠 [Hub](README.md) · [brain.yaml](brain.yaml) · [Prompt.md](Prompt.md) · [Audit.md](Audit.md)

brAIn turns any folder or repository into a **brain-like structure optimized for LLMs**: a small navigation layer (hubs + variables files) routes an AI agent straight to the one file it needs, instead of forcing it to read everything. The result is a radical reduction in token consumption per task.

This document is the specification. The step-by-step transformation algorithm lives in [Prompt.md](Prompt.md), ready-to-copy file templates in [templates/README.md](templates/README.md), and the measurement tool in [tools/brain-audit.md](tools/brain-audit.md).

---

## The 6 rules

### Rule 1 — Folders are connected by a Hub that guides them

Every folder contains a `README.md` that acts as its **hub**: the single entry point an agent reads first. The hub says what the folder is, lists its files with one-line descriptions, and links to the hubs of its subfolders and of its parent. `README.md` is used because GitHub renders it automatically — the hub is ergonomic for humans too.

A hub must contain:

1. **Title + one-line purpose** of the folder.
2. **Navigation header** — link to the parent hub (except at the root) and to the folder's [brain.yaml](brain.yaml).
3. **Files table** — every content file in the folder, linked, with a one-line description.
4. **Subfolders list** — a link to each child folder's `README.md`.

### Rule 2 — Files are connected by hyperlinks

Every content file starts with a **navigation header**: a one-line blockquote linking back to the folder hub, to the folder's `brain.yaml`, and to sibling files it relates to. All links are **relative Markdown links** (`[notes.md](notes.md)`, `[../README.md](../README.md)`), so they work on GitHub, in editors, and for agents alike.

Two integrity constraints follow:

- **No broken links** — every relative link resolves to an existing file.
- **No orphan files** — every file is reachable from the root hub by following links.

### Rule 3 — All files are Markdown

Every content file is `.md`. Text formats (`.txt`, exported `.docx` dumps, notes) are converted to structured Markdown. Markdown is the format LLMs parse most reliably, and it carries hyperlinks (Rule 2) natively.

### Rule 4 — Code lives inside Markdown code fences

Source code is embedded in `.md` files inside fenced blocks with a language tag:

````markdown
## The page

```html
<h1>Salut à tous</h1>
```
````

One `.md` file can hold several fences (e.g. HTML + CSS for one page). The fence's language tag makes extraction trivial — see [tools/brain-audit.md](tools/brain-audit.md) for a one-liner that extracts and runs an embedded script.

### Rule 5 — MCPs and deep configs stay `.json`

Machine-consumed configuration (MCP server definitions, tool configs, lockfile-like data) stays in `.json` files. They don't get converted to Markdown, but they **must be linked** from their folder's hub so they remain reachable (Rule 2). A template is at [templates/skeleton/config.json](templates/skeleton/config.json).

### Rule 6 — Every folder has a `.yaml` with its variables

Each folder carries a `brain.yaml`: a compact, machine-readable card of the folder's variables. An agent that has read the hub and the `brain.yaml` knows exactly which single file to open next — that's the token saving.

---

## `brain.yaml` schema

```yaml
# brain.yaml — folder variables (brAIn rule 6)
name: madame-martin              # folder name
purpose: "Client website for Madame Martin"   # one line
parent: ../brain.yaml            # relative path; null at the project root
children: []                     # subfolders (each has its own README.md + brain.yaml)
files:                           # every content file, with a one-liner
  site.md: "The website — HTML and CSS in code fences"
  todo.md: "Remaining tasks"
when_to_read:                    # scenario routing: question -> file
  "Edit the page or styles": site.md
  "What is left to do?": todo.md
links: {}                        # optional external references (URLs, tickets)
```

All fields are required except `links`. `when_to_read` is the most important field: it is the routing table an agent uses to jump straight to the right file.

## Naming conventions

| Thing | Convention | Example |
|---|---|---|
| Hub | `README.md` (one per folder) | [README.md](README.md) |
| Variables file | `brain.yaml` (one per folder) | [brain.yaml](brain.yaml) |
| Content files | short kebab-case `.md` | `brain-audit.md` |
| Deep configs | `.json`, linked from the hub | `config.json` |
| Nav header | first line of every content file | `> 🧠 [Hub](README.md) · …` |

## How navigation works

````text
|Hub (README.md)-->|----->|folder 1 ------|
                   |----->|folder 2 ------|
                   |----->|folder 3 ------|------>|---->| file 1     |------->|<------|
                   |----->|folder 4 ------|       |---->| file 2     |------->|<------| : all linked by hyperlinks
                   |----->|folder 5 ------|       |---->| file 3     |------->|<------|
                   |----->|folder 6 ------|       |---->| brain.yaml |->variables<----| : especially this one
````

**Cost model.** Without brAIn, an agent looking for one fact must scan the whole folder (`full-scan cost` = sum of all files). With brAIn, it reads the hubs and `brain.yaml` files on the path, then the one target file (`hub-navigation cost`). [Audit.md](Audit.md) shows measured numbers; [tools/brain-audit.md](tools/brain-audit.md) measures any folder.

## Applying brAIn

- **Any LLM**: paste [Prompt.md](Prompt.md) with the target folder.
- **Claude Code**: use the [brainify skill](.claude/skills/brainify/SKILL.md).
- **Verify**: run the auditor from [tools/brain-audit.md](tools/brain-audit.md) — it must report 0 broken links and 0 orphan files.
