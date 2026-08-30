# madame-martin — agent-ready one-page bakery website

> 🧠 [Parent hub](../README.md) · [Variables](brain.yaml)

The project is split by responsibility: agents read the client context and tasks in [Agents/](Agents/README.md), then work on the executable website in [Code/](Code/README.md). The separation gives an agent the information it needs without mixing project knowledge into source files.

```text
after/
|-- Agents/   # requirements, decisions, tasks
|-- Code/     # index.html, style.css
```

## Files

No content files at this level.

## Subfolders

- [Agents/](Agents/README.md) — context that agents read before working
- [Code/](Code/README.md) — real HTML/CSS source files that agents modify
