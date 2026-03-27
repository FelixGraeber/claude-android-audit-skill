---
name: android-audit
description: >
  Full Android audit orchestration. Builds audit-context.json, dispatches
  specialist agents against that shared evidence, then applies canonical
  gate and cap logic. Triggers on: "audit", "full android check",
  "analyze my android project", "project health check".
user-invokable: true
argument-hint: "[path]"
---

# Android Full Audit

## Flow

1. Run `scripts/build_audit_context.py` and write `generated/audit-context.json`
2. Dispatch the relevant agents with that JSON as the shared input
3. Collect category findings and category scores if available
4. Run `scripts/score.py` to apply deterministic gates and caps
5. Generate:
   - `ANDROID-AUDIT-REPORT.md`
   - `ANDROID-ACTION-PLAN.md`

## Reporting Rules

- Separate verified findings from preflight warnings.
- Mark any runtime-only or policy-only claim as `external evidence required`.
- Do not emit a final 0-100 score if category scores were not produced.
