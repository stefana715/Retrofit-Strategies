# CLAUDE.md

> Claude Code reads this file automatically at the start of every session.

## First Steps Every Session
1. Read `docs/project_memory.md` — it has the full project context.
2. Check `docs/decision_log.md` for any recent decisions.
3. Continue from where the TODO list left off.

## Project Overview
- **Paper:** Retrofit strategies + solar + climate change for Changsha residential buildings
- **Target:** Energy and Buildings (Elsevier)
- **Approach:** DOE prototype IDF models + eppy modification + SALib Morris SA + EnergyPlus simulation
- **NO manual building modeling** — we adapt existing prototype IDFs

## Workflow Rules
- Commit and push after every significant action.
- Log what you did in a brief commit message.
- If you create a new script, put it in `code/{stage}/`.
- If you produce a result, put processed data in `data/processed/` and figures in `figure/`.
- Always update the TODO checkboxes in `project_memory.md` when completing a step.

## Current Priority
Check `docs/project_memory.md` → "Immediate TODO" section for the next task.
