---
name: android
description: >
  Android project audit and preflight skill. Builds a shared audit_context.json
  from static project evidence, then uses specialist agents to interpret that
  evidence with explicit confidence and deterministic gate caps. Supports
  Kotlin/Compose and XML/Java repos, including library-only projects. Triggers on:
  "android audit", "android assessment", "android review", "android project health".
---

# Android Project Audit Skill

## Quick Reference

| Command | Description |
|---------|-------------|
| `/android audit [path]` | Full multi-category audit using a shared evidence bundle |
| `/android architecture [path]` | Architecture and module structure review |
| `/android performance [path]` | Static performance preflight |
| `/android security [path]` | OWASP-oriented security audit |
| `/android compat [path]` | Android 15/16 compatibility preflight |
| `/android design [path]` | Design system implementation audit |
| `/android accessibility [path]` | Accessibility preflight from static evidence |
| `/android testing [path]` | Testing strategy and risk coverage review |
| `/android build [path]` | Build system and dependency hygiene review |
| `/android playstore [path]` | Play preflight from source evidence |
| `/android plan [path]` | Prioritized improvement roadmap |

## Consolidated Skill Routing

Use six public skills. Keep the detailed former specialist guides as internal
references so no review knowledge is lost:

- `android`: orchestration, full audit, and planning. Read
  `../android-audit/GUIDE.md` or `../android-plan/GUIDE.md` when needed.
- `android-engineering`: architecture and build system.
- `android-quality`: performance and testing.
- `android-ui`: design and accessibility.
- `android-release`: platform compatibility and Play readiness.
- `android-security`: security.

Do not invoke a `GUIDE.md` file as a separate skill.

## Evidence Contract

The canonical static evidence contract is:

- `schemas/audit_context.schema.json`
- `schemas/finding.schema.json`

The canonical rule registry is:

- `rules/rules.json`
- `rules/facts.json`

Generated markdown references:

- `references/quality-gates.md`
- `references/scoring-weights.md`

Agents should consume `audit-context.json` instead of re-parsing the repo freehand.

## Project Detection

Confirm an Android project by scanning for at least one of:

1. `**/build.gradle.kts` or `**/build.gradle`
2. `**/settings.gradle.kts` or `**/settings.gradle`
3. `**/src/main/AndroidManifest.xml`

If none are present at `[path]`, stop and report that no Android project was detected.

## Project Classification

Classification is deterministic and happens before agent dispatch.

Ordered checks:

1. `sdk-library` if there is no application module and at least one Android library module
2. `single-module` vs `multi-module` from discovered modules
3. `compose-first` vs `xml-legacy` vs `hybrid` from `src/main` sources only

The resulting `project_type` is stored in `audit-context.json` with:

- `repo_kind`
- `app_shape`
- `ui_stack`

## Orchestration Flow

### Step 1: Scan Structure

Run:

```bash
python skills/android/scripts/scan_project.py [path] --json
```

### Step 2: Extract Static Evidence

Run:

```bash
python skills/android/scripts/analyze_gradle.py [path] --json
python skills/android/scripts/analyze_manifest.py [path] --json
python skills/android/scripts/analyze_compose.py [path] --json
python skills/android/scripts/analyze_dependencies.py [path] --json
python skills/android/scripts/check_r8_config.py [path] --json
```

### Step 3: Build Shared Audit Context

Run:

```bash
python skills/android/scripts/build_audit_context.py [path] --output generated/audit-context.json
```

Agents receive `generated/audit-context.json` as their primary input.

### Step 4: Parallel Agent Interpretation

Dispatch relevant agents with:

- project root
- `generated/audit-context.json`
- selected category

Agents must:

- prefer evidence already present in `audit-context.json`
- cite evidence keys and file paths
- mark runtime-only or policy-only claims as lower confidence
- avoid claiming deterministic findings from missing artifacts

### Step 5: Deterministic Gate Evaluation

Apply the canonical gates and caps with:

```bash
python skills/android/scripts/score.py generated/audit-context.json
```

If category scores are available from agents, pass them into `score.py`. Otherwise, emit:

- triggered gates
- unresolved external-evidence gates
- applied score caps
- confidence
- formula trace status

Do not emit a final 0-100 score when category evidence is missing.

## Output Files

Preferred outputs:

- `generated/audit-context.json`
- `ANDROID-AUDIT-REPORT.md`
- `ANDROID-ACTION-PLAN.md`

The report must distinguish:

- `Verified static findings`
- `Preflight warnings`
- `External evidence required`

## Trust Boundaries

These categories are currently static preflight unless richer artifacts are provided:

- Performance: runtime metrics, macrobenchmarks, vitals, traces
- Design system: screenshots, previews, design specs
- Accessibility: runtime semantics, screenshots, assistive-tech testing
- Play preflight: Play Console forms, policy declarations, listing assets

## Freshness

Time-sensitive platform and policy facts live in `rules/facts.json` with:

- `last_verified`
- `source_url`
- `applies_from`
- `confidence`

Do not hardcode moving platform deadlines only in prose.

## Reference Files

- `references/android-16-changes.md`
- `references/owasp-mobile-2024.md`
- `references/play-store-policies.md`
- `references/compose-best-practices.md`
- `references/material-design-3.md`
- `references/quality-gates.md`
- `references/scoring-weights.md`
