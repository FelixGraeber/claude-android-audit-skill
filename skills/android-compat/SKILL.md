---
name: android-compat
description: >
  Android 16 (API 36) compatibility check. Evaluates edge-to-edge enforcement,
  predictive back migration, large screen adaptation, JobScheduler quotas,
  16KB page alignment, and granular health permissions. Triggers on:
  "compatibility", "android 16", "edge-to-edge", "predictive back", "large screen".
user-invokable: true
argument-hint: "[path]"
---

# Android 16 Compatibility Check

Assess readiness for Android 16 (API 36) targeting.

## What This Checks

1. **Target SDK** — `targetSdkVersion >= 36`; timeline compliance
2. **Edge-to-Edge** — `enableEdgeToEdge()` called, proper `WindowInsets` handling, no `windowOptOutEdgeToEdgeEnforcement`, no hardcoded status/nav bar heights, Scaffold with inner padding
3. **Predictive Back** — `android:enableOnBackInvokedCallback="true"` in manifest, no `onBackPressed()` overrides, uses `OnBackPressedCallback` or `OnBackInvokedCallback`, `BackHandler` in Compose
4. **Large Screens** — `WindowSizeClass` usage, no fixed `android:screenOrientation` (non-game apps), no `android:resizableActivity="false"`, responsive layouts
5. **JobScheduler Quotas** — Quota-aware job scheduling, no reliance on `setImportantWhileForeground()` (defunct)
6. **16KB Page Alignment** — Native code `.so` files aligned, `android:pageSizeCompat` if needed
7. **Health Permissions** — Granular permissions (`READ_HEART_RATE`) instead of `BODY_SENSORS`
8. **Intent Security** — `android:intentMatchingFlags` for stricter matching, validated extras

## How to Run

```
/android compat [path]
```

## Scoring

| Factor | Weight |
|--------|--------|
| Target SDK | 20% |
| Edge-to-edge | 20% |
| Predictive back | 15% |
| Large screens | 15% |
| JobScheduler | 10% |
| 16KB pages | 10% |
| Health permissions | 5% |
| Intent security | 5% |

## Reference

Load on-demand: `references/android-16-changes.md`
