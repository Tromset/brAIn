---
name: brainify
description: Transform a folder or repository into a brAIn — hub README.md per folder, brain.yaml variables, all-Markdown files with code in fences, everything hyperlinked. Use when the user says "brainify", "brAInify", or asks to convert a folder into a brAIn / AI-optimized structure.
---

# brainify

Transform the folder the user designates into a brAIn.

1. Read the specification in [brAIn.md](../../../brAIn.md) (the 6 rules, hub convention, `brain.yaml` schema).
2. Follow the step-by-step algorithm in [Prompt.md](../../../Prompt.md) **in order** (inventory → hub tree → hubs + brain.yaml → convert to Markdown → nav links → integrity pass → report). Use the ready-made files in [templates/skeleton/](../../../templates/skeleton/README.md) as starting points.
3. Verify: extract the auditor from [tools/brain-audit.md](../../../tools/brain-audit.md) and run it on the transformed folder. It must report **0 broken links and 0 orphan files**. Include its token table in your report.

If the user only asks for an audit (no transformation), skip to step 3.
