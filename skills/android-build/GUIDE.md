---
name: android-build
description: >
  Build system and dependency hygiene review for Android projects. Focuses on
  module-aware Gradle evidence, KAPT/KSP migration risk, release shrink config,
  repository hygiene, and dependency verification. Triggers on: "build system",
  "gradle", "dependencies", "version catalog", "KAPT", "KSP".
user-invokable: true
argument-hint: "[path]"
---

# Android Build System Review

## What This Checks

1. Version catalogs and inline-version sprawl
2. Convention plugins or shared build logic
3. KAPT usage and likely KSP migration candidates
4. Application release shrink/obfuscation configuration
5. Bad Gradle property overrides such as `android.enableR8.fullMode=false`
6. Repository hygiene, dependency verification, SNAPSHOTs, and wildcard versions

## What This Does Not Check Reliably Yet

- Full Gradle model resolution
- Convention-plugin indirection
- Version freshness without external lookup

## Guidance

- Treat `org.gradle.daemon=true`, `android.nonTransitiveRClass=true`, and similar current defaults as neutral unless explicitly overridden badly.
- Treat `KAPT` as maintenance-mode debt, not as a universal hard failure.
