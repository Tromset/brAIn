# templates.md — Ready-to-copy brAIn files

> 🧠 [Hub](README.md) · [Variables](brain.yaml) · Spec: [brAIn.md](brAIn.md)

The four files a brAInified folder needs, as copy-paste templates. Each implements one or more of the [6 rules](brAIn.md). Copy a fence into the target file, replace every `<placeholder>`, delete what doesn't apply.

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
