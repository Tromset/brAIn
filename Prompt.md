# Prompt.md — The brAIn Transformation Prompt

> 🧠 [Hub](README.md) · [brain.yaml](brain.yaml) · Spec: [brAIn.md](brAIn.md) · Verify with: [tools/brain-audit.md](tools/brain-audit.md)

Copy everything below the line into any LLM (Claude, ChatGPT, Gemini, Qwen, Llama, Gemma…) together with access to the target folder. The algorithm is deterministic: same folder in, same structure out. Claude Code users can invoke it directly via the [brainify skill](.claude/skills/brainify/SKILL.md).

---

You are transforming the folder I give you into a **brAIn**: a brain-like structure where an AI agent can find any fact by reading a hub, a variables file, and one target file — instead of scanning everything. Apply the 6 rules below by following the steps **in order**. Do not skip the integrity pass.

**The 6 rules**

1. Folders are connected by a Hub that guides them (`README.md` in every folder).
2. Files are connected by hyperlinks (relative Markdown links, no broken links, no orphans).
3. All content files are Markdown (`.md`).
4. Code lives inside the `.md` files, in fenced blocks with a language tag.
5. MCPs and deep configs stay `.json`, linked from the hub.
6. Every folder has a `brain.yaml` describing its variables.

**Step 0 — Scope and safety.**
Never touch `.git/`, hidden folders, binaries, or lockfiles. Work on a copy or a branch if the folder is a live project. List anything you decide to leave untouched and say why.

**Step 1 — Inventory.**
Walk the folder. For every file record: path, type, size, and a one-line summary of what it contains. For every subfolder record its purpose. This inventory drives every later step.

**Step 2 — Design the hub tree.**
Decide the folder structure first. Keep the existing hierarchy unless it is clearly wrong; merge folders with a single tiny file into their parent. Every remaining folder will get a `README.md` (hub) and a `brain.yaml`. Draw the target tree before creating anything.

**Step 3 — Create the hub and variables file of every folder.**
For each folder, create:

- `README.md` — title + one-line purpose; a nav header linking the parent hub and the folder's `brain.yaml`; a table of every content file with a one-line description; a linked list of subfolder hubs.
- `brain.yaml` — following this schema exactly:

```yaml
name: <folder-name>
purpose: "<one line>"
parent: ../brain.yaml        # null at the root
children: [<subfolder>/, ...]
files:
  <file.md>: "<one-liner>"
when_to_read:
  "<question an agent might have>": <file.md>
links: {}
```

`when_to_read` must cover the questions someone is most likely to bring to this folder.

**Step 4 — Convert content files to Markdown.**
For every non-`.md` text file:

- Plain text / notes / exported docs → structured `.md` (headings, lists), same information, nothing invented.
- Source code (`.html`, `.css`, `.py`, …) → embed in a `.md` file inside a fenced block tagged with the language. Group related code (e.g. one page's HTML + CSS) into one file with several fences.
- `.json` deep configs → **keep as `.json`** (rule 5), just link them from the hub.
- Merge redundant fragments (e.g. `brief.txt` + `notes.txt` about the same subject) into one `.md` with sections, and say so in the file.

Delete the originals only after their content is fully carried over; otherwise keep them and flag the duplication.

**Step 5 — Add navigation links to every file.**
Every content `.md` file starts with a one-line nav header:

```markdown
> 🧠 [Hub](README.md) · [Variables](brain.yaml) · Related: [<sibling>.md](<sibling>.md)
```

Add inline links wherever one file mentions another. All links are relative.

**Step 6 — Integrity pass.**
Verify, and fix until all three hold:

1. Every relative Markdown link resolves to an existing file (**0 broken links**).
2. Every file is reachable from the root `README.md` by following links (**0 orphan files**).
3. Every folder has exactly one `README.md` and one `brain.yaml`, and every file listed in a `brain.yaml` exists.

If the brAIn repo's auditor is available, run it to confirm: extract and run the script from `tools/brain-audit.md` on the folder root.

**Step 7 — Report.**
Output: the final tree, the list of conversions/merges performed, anything left untouched (with reason), and the integrity results.
