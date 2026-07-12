# brAIn

*Turn any folder or repository into an AI paradise.*

> 🧠 This README is the repo's **Hub** · [brain.yaml](brain.yaml) · Spec: [brAIn.md](brAIn.md) · Prompt: [Prompt.md](Prompt.md) · Numbers: [Audit.md](Audit.md)

brAIn gives a project a **brain-like structure for LLMs**: folders connected by a Hub, files connected by hyperlinks, everything in Markdown, and a variables file in every folder. An agent finds any fact by reading a hub, a `brain.yaml`, and **one** target file — instead of scanning the whole project. Result: **radical token-consumption reduction**, [measured](Audit.md).

Works with any LLM: [Claude](https://claude.ai/), [ChatGPT](https://chatgpt.com), [Gemini](https://gemini.google.com), [Qwen](https://github.com/QwenLM/Qwen), [Llama](https://github.com/meta-llama/llama), [Gemma](https://github.com/google-deepmind/gemma).

## The 6 rules

1. **Folders are connected by a Hub that guides them** — a `README.md` in every folder.
2. **Files are connected by hyperlinks** — relative Markdown links; no broken links, no orphans.
3. **All files are Markdown** (`.md`).
4. **Code lives inside the `.md` files**, in fenced blocks with a language tag.
5. **MCPs and deep configs stay `.json`**, linked from the hub.
6. **Every folder has a `.yaml`** (`brain.yaml`) **with the folder's variables** — including a `when_to_read` routing table.

Full detail in the spec: [brAIn.md](brAIn.md).

## How it navigates

````text
|Hub (README.md)-->|----->|folder 1 ------|
                   |----->|folder 2 ------|
                   |----->|folder 3 ------|------>|---->| file 1     |------->|<------|
                   |----->|folder 4 ------|       |---->| file 2     |------->|<------| : all linked by hyperlinks
                   |----->|folder 5 ------|       |---->| file 3     |------->|<------|
                   |----->|folder 6 ------|       |---->| brain.yaml |->variables<----| : especially this one
````

## Quickstart

**Any LLM** — paste [Prompt.md](Prompt.md) together with access to your folder; the algorithm is step-by-step and deterministic.

**Claude Code** — this repo ships a skill: say *"brainify this folder"* (see [.claude/skills/brainify/SKILL.md](.claude/skills/brainify/SKILL.md)).

**Starting a folder by hand** — copy [templates/skeleton/](templates/skeleton/README.md) into it and fill the placeholders.

**Measure & verify** — extract the stdlib-only auditor from [tools/brain-audit.md](tools/brain-audit.md):

```bash
awk '/^```python$/{code=1; next} /^```$/{code=0} code' tools/brain-audit.md > brain_audit.py
python3 brain_audit.py <your-folder>   # tokens, scan-vs-navigation savings, link integrity
```

## Proof

The demo in [examples/madame-martin/](examples/madame-martin/README.md) shows the same mini-project before and after brAIn: per-lookup costs drop **7–58% even on a 5-file toy project**, and the saving grows with project size. Methodology and full tables: [Audit.md](Audit.md).

## Repo map

This repo dogfoods its own rules — every folder has a hub and a `brain.yaml`, and every file below is reachable from here.

| Path | What it is |
|---|---|
| [brAIn.md](brAIn.md) | The technology spec: the 6 rules in detail, hub convention, `brain.yaml` schema |
| [Prompt.md](Prompt.md) | The transformation prompt — copy-paste into any LLM to brAInify a folder |
| [Audit.md](Audit.md) | Measurement methodology + demo audit results |
| [templates/](templates/README.md) | Ready-to-copy skeleton files (hub, `brain.yaml`, content file, config) |
| [examples/](examples/README.md) | Before/after demos — currently [madame-martin/](examples/madame-martin/README.md) |
| [tools/](tools/README.md) | The auditor, embedded in Markdown per rule 4 |
| [.claude/skills/brainify/](.claude/skills/brainify/SKILL.md) | Claude Code skill wrapping the prompt |
| [Croquis-brAIn.md](Croquis-brAIn.md) | The original project sketch (French, historical) |
| [brain.yaml](brain.yaml) | This folder's variables (rule 6) |

## References

- Claude — <https://claude.ai/>
- ChatGPT — <https://chatgpt.com>
- Gemini — <https://gemini.google.com>
- Qwen — <https://github.com/QwenLM/Qwen>
- Llama — <https://github.com/meta-llama/llama>
- Gemma — <https://github.com/google-deepmind/gemma>
