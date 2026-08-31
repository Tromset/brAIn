# brAIn

*Turn any folder or repository into an AI paradise.*

> 🧠 This README is the repo's **Hub** · [brain.yaml](brain.yaml) · Spec: [brAIn.md](brAIn.md) · Skill: [Skill.md](Skill.md) · Numbers: [Audit.md](Audit.md)

brAIn gives a project a **brain-like structure for LLMs**: folders connected by a Hub, files connected by hyperlinks, everything in Markdown, and a variables file in every folder. An agent finds any fact by reading a hub, a `brain.yaml`, and **one** target file — instead of scanning the whole project. Result: **radical token-consumption reduction**, [measured](Audit.md).

Works with any LLM: [Claude](https://claude.ai/), [ChatGPT](https://chatgpt.com), [Gemini](https://gemini.google.com), [Qwen](https://github.com/QwenLM/Qwen), [Llama](https://github.com/meta-llama/llama), [Gemma](https://github.com/google-deepmind/gemma).

## The 6 rules

1. **Folders are connected by a Hub that guides them** — a `README.md` in every folder.
2. **Files are connected by hyperlinks** — relative Markdown links; no broken links, no orphans.
3. **All files are Markdown** (`.md`).
4. **Code lives inside the "Code" folder of any main folder in the project.**
5. **MCPs and deep configs stay** `.json`, linked from the hub.
6. **Every folder has a** `.yaml` (`brain.yaml`) **with the folder's variables** — including a `when_to_read` routing table.

Full detail in the spec: [brAIn.md](brAIn.md).

## How it navigates

```text
|Hub (README.md)-->|----->|folder 1 ------|
                   |----->|folder 2 ------|
                   |----->|folder 3 ------|------>|---->| file 1     |------->|<------|
                   |----->|folder 4 ------|       |---->| file 2     |------->|<------| : all linked by hyperlinks
                   |----->|folder 5 ------|       |---->| file 3     |------->|<------|
                   |----->|folder 6 ------|       |---->| brain.yaml |->variables<----| : especially this one
```



## Quickstart

**Any LLM / agent** — give it [Skill.md](Skill.md) together with access to your folder; the workflow is step-by-step and deterministic. In Claude Code or Cursor, say *"brainify this folder"*.

**Starting a folder by hand** — copy the four templates from [templates.md](templates.md) and fill the placeholders.

**CLI (recommended)** — brAInify any folder with styled progress bars, then audit:

```bash
./brainify                                          # Finder picker → brAInify the chosen folder
./brainify --no-split                               # picker, keep layout (no Agents/ + Code/)
python3 scripts/brainify.py <your-folder>           # Agents/Code split + hubs + yaml + audit
python3 scripts/brain_audit.py <your-folder>        # tokens, savings, link integrity
```

Details: [scripts/](scripts/README.md). The auditor also lives embedded in [Audit.md](Audit.md) (rule 4).

## Proof

The demo in [examples/](examples/README.md) shows the same mini-project before and after brAIn: per-lookup costs drop **7–35% even on a 5-file toy project**, and the saving grows with project size. Methodology and full tables: [Audit.md](Audit.md).

## Repo map

This repo dogfoods its own rules — every folder has a hub and a `brain.yaml`, and every file below is reachable from here.


| Path                            | What it is                                                                       |
| ------------------------------- | -------------------------------------------------------------------------------- |
| [brAIn.md](brAIn.md)            | The technology spec: the 6 rules in detail, hub convention, `brain.yaml` schema  |
| [Skill.md](Skill.md)            | The brainify skill — workflow + templates to brAInify any folder                 |
| [Audit.md](Audit.md)            | Measurement methodology, demo results + the auditor itself (embedded per rule 4) |
| [templates.md](templates.md)    | Ready-to-copy templates (hub, `brain.yaml`, content file, config)                |
| [examples/](examples/README.md) | Before/after demo — the "Site Madame Martin" mini-project                        |
| [brainify](./brainify)          | Launcher — Finder folder picker → `scripts/brainify.py`                          |
| [scripts/](scripts/README.md)   | CLI — `brainify.py` (progress UI) + `brain_audit.py`                             |
| [brain.yaml](brain.yaml)        | This folder's variables (rule 6)                                                 |




## References

- Claude — [https://claude.ai/](https://claude.ai/)
- ChatGPT — [https://chatgpt.com](https://chatgpt.com)
- Gemini — [https://gemini.google.com](https://gemini.google.com)
- Qwen — [https://github.com/QwenLM/Qwen](https://github.com/QwenLM/Qwen)
- Llama — [https://github.com/meta-llama/llama](https://github.com/meta-llama/llama)
- Gemma — [https://github.com/google-deepmind/gemma](https://github.com/google-deepmind/gemma)

