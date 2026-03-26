---
name: android-audit
description: >
  Full Android project audit with parallel subagent delegation. Scans project
  structure, dispatches 9 specialized agents, aggregates into health score 0-100,
  generates prioritized action plan. Triggers on: "audit", "full android check",
  "analyze my android project", "project health check".
user-invokable: true
argument-hint: "[path]"
---

# Android Full Audit

Comprehensive project audit using 9 parallel specialized agents.

## How to Run

```
/android audit [path]
```

## Orchestration

This sub-skill is invoked by the main `/android` skill when the `audit` command is used. It follows the 6-step orchestration flow defined in the main `android/SKILL.md`.

1. **Scan** — `scan_project.py` discovers structure
2. **Extract** — `analyze_gradle.py` + `analyze_manifest.py` get config
3. **Classify** — Detect app type
4. **Dispatch** — 9 agents in parallel
5. **Aggregate** — Weighted score
6. **Report** — Two markdown files

## Output Files

- `ANDROID-AUDIT-REPORT.md` — Executive summary + per-category findings
- `ANDROID-ACTION-PLAN.md` — Prioritized recommendations (Critical → Low)
