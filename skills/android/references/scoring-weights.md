# Scoring Weights -- Generated from rules/rules.json

This file is generated from the canonical registry at `skills/android/rules/rules.json`.

## Category Weights

| Category | Weight | Mode |
|---|---|---|
| Architecture | 15% | audit |
| Performance | 15% | audit |
| Security | 15% | audit |
| Compatibility | 10% | audit |
| Design System Implementation | 10% | preflight_until_visual_artifacts |
| Accessibility | 10% | preflight_until_runtime_artifacts |
| Testing | 10% | audit |
| Build System | 10% | audit |
| Play Preflight | 5% | preflight_until_console_artifacts |

## Score Policy

- Overall formula: `sum(category_score * weight / 100)`
- Requires category scores: `True`
- Insufficient evidence behavior: Do not emit a final 0-100 score when category evidence is missing; emit confidence and gate results instead.

## Gate Summary

| Severity | Count |
|---|---|
| critical | 8 |
| high | 8 |
