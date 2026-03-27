---
name: android-compat
description: >
  Android 15/16 compatibility preflight. Evaluates target SDK posture,
  edge-to-edge signals, predictive back migration risk, large-screen behavior,
  and 16 KB page-size readiness with explicit version awareness. Triggers on:
  "compatibility", "android 16", "edge-to-edge", "predictive back", "large screen".
user-invokable: true
argument-hint: "[path]"
---

# Android Compatibility Preflight

## What This Checks

1. Current target SDK posture against canonical dated facts in `rules/facts.json`
2. Edge-to-edge implementation signals
3. Legacy `onBackPressed()` usage and predictive-back migration risk
4. Large-screen restriction risks that become weaker or invalid on newer API targets
5. 16 KB page-size readiness signals when native code is present

## Version-Aware Rules

- Do not reward `android:enableOnBackInvokedCallback="true"` as a blanket positive.
- Treat that manifest flag as a temporary opt-out concern when targeting Android 16 behavior.
- Treat large-screen orientation and resizability restrictions as compatibility risks, not timeless best-practice deductions.
- Treat 16 KB page-size readiness as a release-risk input, not an optional future note.
