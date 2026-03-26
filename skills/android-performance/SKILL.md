---
name: android-performance
description: >
  Performance assessment for Android projects. Evaluates Baseline Profiles,
  R8 configuration, app startup optimization, Compose recomposition patterns,
  memory management, ANR prevention, and APK/AAB size. Triggers on:
  "performance", "baseline profile", "startup", "recomposition", "ANR", "APK size".
user-invokable: true
argument-hint: "[path]"
---

# Android Performance Assessment

Evaluate performance optimization posture of an Android project.

## What This Checks

1. **Baseline Profiles** — `baseline-prof.txt` or benchmark module with `BaselineProfileRule`
2. **Startup Profiles** — `startup-prof.txt` existence
3. **R8 Configuration** — `minifyEnabled`, `shrinkResources`, R8 full mode, ProGuard rules quality
4. **App Startup** — App Startup library usage, content provider consolidation, lazy initialization
5. **Compose Recomposition** — `@Stable`/`@Immutable`, `derivedStateOf`, `key()` in LazyColumn, `remember`, strong skipping mode
6. **Memory Management** — LeakCanary integration, StrictMode VmPolicy, no static Context references
7. **ANR Prevention** — No main-thread I/O, coroutines with proper dispatchers, `goAsync()` for receivers
8. **APK/AAB Size** — AAB format, resource shrinking, WebP images, limited language resources

## How to Run

```
/android performance [path]
```

## Process

1. Run `scripts/scan_project.py` and `scripts/analyze_gradle.py`
2. Run `scripts/check_r8_config.py` for ProGuard/R8 analysis
3. Run `scripts/analyze_compose.py --mode stability` for recomposition patterns
4. Check for Baseline Profile files and benchmark module
5. Grep for performance anti-patterns

## Scoring

| Factor | Weight |
|--------|--------|
| Baseline Profiles | 20% |
| Compose recomposition | 20% |
| R8/shrinking | 15% |
| App startup | 15% |
| Memory management | 15% |
| APK/AAB size | 15% |

## Key Thresholds

| Metric | Good | Warning | Bad |
|--------|------|---------|-----|
| Cold start | <2s | 2-5s | >=5s |
| Warm start | <1s | 1-2s | >=2s |
| Hot start | <0.5s | 0.5-1.5s | >=1.5s |
| Crash rate | <0.5% | 0.5-1.09% | >=1.09% |
| ANR rate | <0.1% | 0.1-0.47% | >=0.47% |

## Reference

Load on-demand: `references/vitals-thresholds.md`, `references/compose-best-practices.md`
