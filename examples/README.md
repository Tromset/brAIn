# examples/ — the "Site Madame Martin" demo

> 🧠 [Parent hub](../README.md) · [Variables](brain.yaml) · Full audit: [../Audit.md](../Audit.md)

A fictional mini-project (see the spec, [brAIn.md](../brAIn.md)): a one-page bakery website for Mme Martin, shown twice with the **same information content** —

- [before/](#before--the-typical-messy-folder) — the typical messy project folder (no index, opaque filenames)
- [after/](after/README.md) — the same project with brAIn navigation plus the `Agents/` / `Code/` workflow from [Prompt.md](../Prompt.md)

## before/ — the typical messy folder

No hub, no variables file: an agent looking for one fact has no index and must read everything.

| File | What it turns out to contain |
|---|---|
| [before/index.html](before/index.html) | The page |
| [before/style.css](before/style.css) | The styles |
| [before/brief.txt](before/brief.txt) | Client brief (a `.docx` dump, formatting lost) |
| [before/notes.txt](before/notes.txt) | Working notes — partly duplicating the brief |
| [before/todo.txt](before/todo.txt) | Task list |

## after/ — agent-ready

[after/README.md](after/README.md) is the hub; [after/brain.yaml](after/brain.yaml) routes every question to the right folder and file:

- [after/Agents/](after/Agents/README.md) contains the merged [client context](after/Agents/notes.md) and [task list](after/Agents/todo.md) that agents read.
- [after/Code/](after/Code/README.md) contains the real, executable [HTML](after/Code/index.html) and [CSS](after/Code/style.css) files that agents modify.

The Markdown hubs and `brain.yaml` files wrap the project with a navigation layer while the deployable source remains executable as-is.

## Measured result

Numbers from the auditor in [Audit.md](../Audit.md) (chars ÷ 3.5 heuristic), full tables there:

| Lookup scenario | before (full scan) | after (hub navigation) | Savings |
|---|---:|---:|---:|
| "What is left to do?" | 1179 | 770 | 34.7% |
| "What did the client ask for?" | 1179 | 1089 | 7.6% |
| "Edit the page structure or wording" | 1179 | 954 | 19.1% |
| "Edit the styles or responsive layout" | 1179 | 831 | 29.5% |
