---
name: android-playstore
description: >
  Google Play preflight from source evidence. Evaluates target SDK posture,
  foreground service declarations, permission surface, and obvious policy red flags
  without claiming full Play Console compliance. Triggers on: "play store",
  "target SDK", "data safety", "foreground service", "play policy".
user-invokable: true
argument-hint: "[path]"
---

# Play Preflight

## Scope

This is a source-code preflight, not full Play Store readiness.

It can help with:

1. target SDK posture
2. foreground service type declarations
3. suspicious permission surface
4. obvious debug or manifest risks

It cannot prove:

- Data Safety form correctness
- privacy policy completeness
- account deletion flow compliance
- families, health, finance, or medical declarations
- store listing asset quality

Use dated facts from `rules/facts.json` for deadline-sensitive guidance.
