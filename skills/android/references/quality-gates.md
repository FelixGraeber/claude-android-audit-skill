# Quality Gates -- Generated from rules/rules.json

This file is generated from the canonical registry at `skills/android/rules/rules.json`.

## Critical Severity

| ID | Category | Rule | External Evidence Required | Cap Behavior |
|---|---|---|---|---|
| C1 | security | Exported component without protective permission | No | cap_final_score_40 |
| C2 | security | Cleartext traffic enabled without network security config | No | cap_final_score_40 |
| C3 | play_preflight | Target SDK below current Play submission requirement | No | cap_final_score_40 |
| C4 | security | Hardcoded secrets in source | No | cap_final_score_40 |
| C5 | performance | Crash rate above Android Vitals bad behavior threshold | Yes | cap_final_score_40 |
| C6 | performance | ANR rate above Android Vitals bad behavior threshold | Yes | cap_final_score_40 |
| C7 | build_system | Application release build lacks shrink/obfuscation | No | cap_final_score_40 |
| C8 | security | Manifest debuggable enabled | No | cap_final_score_40 |

## High Severity

| ID | Category | Rule | External Evidence Required | Cap Behavior |
|---|---|---|---|---|
| H1 | build_system | KAPT still in use where KSP is likely available | No | counts_toward_high_cap |
| H2 | performance | No benchmark or baseline profile module detected | No | counts_toward_high_cap |
| H3 | accessibility | Low-confidence touch target risk | No | counts_toward_high_cap |
| H4 | security | Deprecated security-crypto dependency still present | No | counts_toward_high_cap |
| H5 | compatibility | No edge-to-edge implementation evidence | No | counts_toward_high_cap |
| H6 | security | No network security config | No | counts_toward_high_cap |
| H7 | security | WebView SSL errors potentially ignored | No | counts_toward_high_cap |
| H8 | compatibility | Legacy onBackPressed override without Android 16 migration | No | counts_toward_high_cap |

## Score Caps

| ID | When | Max Score |
|---|---|---|
| critical-cap | any_critical_gate_triggered | 40 |
| high-cap | high_gate_count >= 3 | 60 |

## Notes

- Final scores require category scores plus gate evaluation.
- External-evidence gates stay unresolved until telemetry or store artifacts are provided.
- Preflight categories should report lower confidence when runtime or visual artifacts are missing.
