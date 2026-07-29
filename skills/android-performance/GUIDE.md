---
name: android-performance
description: >
  Android performance preflight. Focuses on static build and source signals such
  as benchmark modules, baseline-profile setup, shrink config, and Compose
  recomposition hints. It does not claim runtime startup or ANR scores without
  external artifacts.
user-invokable: true
argument-hint: "[path]"
---

# Android Performance Preflight

## Static Checks

1. Benchmark or macrobenchmark modules
2. Baseline-profile evidence
3. Release shrink and optimization configuration
4. Compose recomposition hints such as `derivedStateOf`, lazy keys, and lifecycle-aware state collection
5. Debug tools such as StrictMode and LeakCanary

## External Evidence Required

- cold, warm, and hot startup timings
- ANR risk scoring
- frame timing and jank
- APK or AAB size claims against release outputs
- Compose compiler metrics
- Perfetto or startup traces
