---
name: android-playstore
description: >
  Play Store readiness check for Android projects. Evaluates target SDK
  compliance, data safety signals, foreground service types, Google Play
  policy compliance, and ASO basics. Triggers on: "play store", "target SDK",
  "data safety", "foreground service", "play policy".
user-invokable: true
argument-hint: "[path]"
---

# Play Store Readiness Check

Evaluate Google Play Store compliance and distribution readiness.

## What This Checks

1. **Target SDK** — Meets Play Store deadline: 35+ required Aug 2025, 36+ expected Aug 2026
2. **Foreground Service Types** — All foreground services declare `foregroundServiceType` (Android 14+), correct type-specific permissions
3. **Data Safety** — Permission audit: declared permissions vs actual usage, unnecessary permissions flagged
4. **Policy Compliance** — `android:debuggable` not true in release, proper content rating implications, API declarations
5. **Permissions Audit** — Minimal permissions, runtime permissions requested contextually, alternatives used where possible (Photo Picker vs READ_EXTERNAL_STORAGE)
6. **ASO Basics** — App label from manifest, version name meaningful, proper icon configuration

## How to Run

```
/android playstore [path]
```

## Process

1. Run `scripts/analyze_gradle.py` for targetSdk, versionCode, versionName
2. Run `scripts/analyze_manifest.py` for permissions, FGS types, component analysis
3. Cross-reference permissions with source code usage
4. Check for Play Store policy red flags

## Scoring

| Factor | Weight |
|--------|--------|
| Target SDK compliance | 25% |
| Foreground service types | 15% |
| Data safety signals | 15% |
| Policy compliance | 15% |
| Permissions audit | 15% |
| ASO basics | 15% |

## Target SDK Timeline

| Deadline | Requirement |
|----------|-------------|
| Aug 31, 2025 | New apps and updates must target API 35 |
| ~Aug 2026 | Expected: must target API 36 |

## Foreground Service Types (Android 14+)

Must declare in manifest: `camera`, `connectedDevice`, `dataSync`, `health`, `location`, `mediaPlayback`, `mediaProjection`, `microphone`, `phoneCall`, `remoteMessaging`, `shortService`, `specialUse`, `systemExempted`, `mediaProcessing`

## Reference

Load on-demand: `references/play-store-policies.md`
