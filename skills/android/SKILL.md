---
name: android
description: >
  Comprehensive Android project assessment. Analyzes architecture patterns,
  performance optimization, security posture, Android 16 compatibility,
  Material Design compliance, accessibility, testing strategy, build system
  health, and Play Store readiness. Supports Kotlin/Compose and legacy
  XML/Java projects. Triggers on: "android audit", "android assessment",
  "android review", "android project health", "android security",
  "android performance", "android compatibility".
user-invokable: true
argument-hint: "[command] [path]"
---

# Android Project Assessment Skill

## Quick Reference

| Command | Description |
|---------|-------------|
| `/android audit [path]` | Full 9-category audit with scores and action plan |
| `/android architecture [path]` | Architecture patterns only (Compose, UDF, DI, Nav) |
| `/android performance [path]` | Performance only (Baseline Profiles, R8, recomposition) |
| `/android security [path]` | Security only (OWASP Mobile Top 10 2024) |
| `/android compat [path]` | Android 16 (API 36) compatibility check |
| `/android design [path]` | Material Design 3 / M3 Expressive compliance |
| `/android accessibility [path]` | Accessibility audit (touch targets, semantics, contrast) |
| `/android testing [path]` | Testing strategy and coverage assessment |
| `/android build [path]` | Build system health (Gradle, AGP, catalogs) |
| `/android playstore [path]` | Play Store readiness and policy compliance |
| `/android score [path]` | Quick overall score without detailed findings |

## Project Detection

Scan for presence of these files to confirm an Android project:

1. `**/build.gradle.kts` or `**/build.gradle` (root and module level)
2. `**/settings.gradle.kts` or `**/settings.gradle`
3. `**/AndroidManifest.xml`
4. `**/gradle/libs.versions.toml` (version catalog)

If none found at `[path]`, report error and stop.

## App Type Classification

Determine project type before dispatching agents — agents adapt checks accordingly.

| Type | Detection Criteria |
|------|-------------------|
| `single-module` | Only one module with `com.android.application` plugin |
| `multi-module` | Multiple modules in `settings.gradle.kts` includes |
| `compose-first` | `compose = true` in build config, Compose dependencies, no/minimal XML layouts |
| `xml-legacy` | XML layouts present, no Compose dependencies |
| `hybrid` | Both Compose and XML layouts coexist |
| `sdk-library` | `com.android.library` plugin only, no application module |

Classification uses ordered checks:
1. Count modules from `settings.gradle.kts` → single vs multi
2. Check for `compose` in build files → compose-first vs xml-legacy vs hybrid
3. Check for `com.android.library` without `com.android.application` → sdk-library

## Audit Orchestration Flow

### Step 1: Project Scan
```
Glob: **/build.gradle.kts, **/settings.gradle.kts, **/AndroidManifest.xml
Glob: **/gradle/libs.versions.toml
Glob: **/src/main/**/*.kt, **/src/main/**/*.java
Glob: **/src/main/res/layout/**/*.xml
```

### Step 2: Config Extraction
Read root `build.gradle.kts` and `libs.versions.toml` to extract:
- `compileSdk`, `targetSdk`, `minSdk`
- AGP version, Kotlin version, Compose BOM version
- Key dependency versions (Hilt, Navigation, Lifecycle, etc.)

### Step 3: Type Detection
Apply classification rules from the table above. Store as `APP_TYPE`.

### Step 4: Parallel Agent Dispatch
Dispatch all 9 agents in parallel using the Agent tool. Each agent receives:
- Project root path
- `APP_TYPE` classification
- Extracted config (SDK versions, dependencies)
- Specific file patterns to analyze

```
Agent: android-architecture  → Architecture score + findings
Agent: android-performance   → Performance score + findings
Agent: android-security      → Security score + findings
Agent: android-compat        → Compatibility score + findings
Agent: android-design        → Design score + findings
Agent: android-accessibility → Accessibility score + findings
Agent: android-testing       → Testing score + findings
Agent: android-build         → Build system score + findings
Agent: android-playstore     → Play Store score + findings
```

For single-category commands (e.g., `/android security`), dispatch only the relevant agent.

### Step 5: Score Aggregation

Collect scores from all agents and compute weighted overall score.

| Category | Weight | Agent |
|----------|--------|-------|
| Architecture | 15% | android-architecture |
| Performance | 15% | android-performance |
| Security | 15% | android-security |
| Compatibility | 10% | android-compat |
| Design | 10% | android-design |
| Accessibility | 10% | android-accessibility |
| Testing | 10% | android-testing |
| Build System | 10% | android-build |
| Play Store | 5% | android-playstore |

**Overall Score** = Σ (category_score × weight)

Score interpretation:
- **90-100**: Production-ready, best practices followed
- **70-89**: Good shape, minor improvements needed
- **50-69**: Significant gaps, prioritize high-weight categories
- **Below 50**: Major issues, consider architectural remediation

### Step 6: Report Generation

Generate two files:

**ANDROID-AUDIT-REPORT.md** — Full assessment with:
- Executive summary (overall score, app type, key metrics)
- Per-category breakdown (score, findings, severity)
- Dependency version table
- Architecture diagram (text-based)

**ANDROID-ACTION-PLAN.md** — Prioritized remediation with:
- Critical issues (must fix before release)
- High priority (fix within next sprint)
- Medium priority (plan for next quarter)
- Low priority (nice to have)
- Estimated effort per item (S/M/L/XL)

## Quality Gates

### Critical (blocks release)
- `targetSdk` < 35 (Play Store requirement Aug 2025)
- Cleartext traffic allowed without exception
- Exported components without permissions
- Hardcoded secrets in source
- `minSdk` < 24 without compelling reason
- Missing `foregroundServiceType` on Android 14+ services

### High (fix before next release)
- No Baseline Profiles
- No R8/ProGuard configuration
- KAPT still used where KSP is available
- No test coverage at all
- Deprecated `onBackPressed` without migration
- `SharedPreferences` for sensitive data
- Hardcoded colors instead of Material color roles

## Error Handling

| Error | Resolution |
|-------|-----------|
| No Android project found at path | Report: "No Android project detected. Expected build.gradle.kts and AndroidManifest.xml." |
| Gradle files unparseable | Fall back to regex-based extraction, flag reduced accuracy |
| Agent timeout | Report partial results, mark timed-out category as "incomplete" |
| Mixed build systems (Gradle + other) | Analyze Gradle portions only, note in report |
| Empty source directories | Score as 0 for relevant categories, flag as "no source to analyze" |

## Cross-References

- For detailed Material 3 Expressive token guidance: `/material-3-expressive`
- For comprehensive Android design patterns: `/android-design-guidelines`
- For ASO and store listing optimization: `/aso audit`

## Available Tools

| Tool | Usage |
|------|-------|
| `Read` | Read build files, source code, manifests, configs |
| `Bash` | Run Gradle tasks, count files, check versions |
| `Write` | Generate report and action plan files |
| `Glob` | Find project files by pattern |
| `Grep` | Search source code for patterns, anti-patterns, API usage |
| `Agent` | Dispatch specialist agents for parallel analysis |

## Reference Files (loaded on-demand by agents)

- `references/android-16-changes.md` — Android 16 behavioral changes and migration guide
- `references/owasp-mobile-2024.md` — OWASP Mobile Top 10 (2024) checklist
- `references/play-store-policies.md` — Current Play Store policy requirements
- `references/compose-performance.md` — Compose recomposition optimization guide
- `references/material-3-tokens.md` — M3 token reference and mapping
