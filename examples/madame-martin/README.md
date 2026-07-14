# madame-martin — the "Site Madame Martin" demo

> 🧠 [Parent hub](../README.md) · [Variables](brain.yaml) · Full audit: [../../Audit.md](../../Audit.md)

The fictional mini-project from the original sketch (see the spec, [brAIn.md](../../brAIn.md)): a one-page bakery website for Mme Martin, shown twice with the **same information content** —

- [before/](#before--the-typical-messy-folder) — the typical messy project folder (no index, opaque filenames)
- [after/](after/README.md) — the same project brAInified per the [6 rules](../../brAIn.md)

## before/ — the typical messy folder

No hub, no variables file: an agent looking for one fact has no index and must read everything.

| File | What it turns out to contain |
|---|---|
| [before/index.html](before/index.html) | The page |
| [before/style.css](before/style.css) | The styles |
| [before/brief.txt](before/brief.txt) | Client brief (a `.docx` dump, formatting lost) |
| [before/notes.txt](before/notes.txt) | Working notes — partly duplicating the brief |
| [before/todo.txt](before/todo.txt) | Task list |

## after/ — brAInified

[after/README.md](after/README.md) is the hub; [after/brain.yaml](after/brain.yaml) routes every question to one file. HTML + CSS live in [after/site.md](after/site.md) (code fences, rule 4); brief and notes are merged into [after/notes.md](after/notes.md); tasks in [after/todo.md](after/todo.md).

## Measured result

Numbers from [tools/brain-audit.md](../../tools/brain-audit.md) (chars ÷ 3.5 heuristic), full tables in [Audit.md](../../Audit.md):

| Lookup scenario | before (full scan) | after (hub navigation) | Savings |
|---|---:|---:|---:|
| "What is left to do?" | 1179 | 492 | 58.3% |
| "What did the client ask for?" | 1179 | 811 | 31.2% |
| "Edit the page or styles" | 1179 | 1097 | 7.0% |
