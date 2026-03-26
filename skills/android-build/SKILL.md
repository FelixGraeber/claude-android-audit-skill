---
name: android-build
description: >
  Build system and dependencies review for Android projects. Analyzes Gradle
  version catalogs, convention plugins, KSP vs KAPT, R class transitivity,
  build performance, and dependency verification. Triggers on: "build system",
  "gradle", "dependencies", "version catalog", "KAPT", "KSP".
user-invokable: true
argument-hint: "[path]"
---

# Android Build System Review

Evaluate build system health, dependency management, and build performance.

## What This Checks

1. **Version Catalogs** — `gradle/libs.versions.toml` exists and is used (vs inline versions)
2. **Convention Plugins** — `build-logic/` directory with shared build configuration
3. **KSP over KAPT** — No `kotlin-kapt` plugin when KSP alternative exists (Hilt, Room, Moshi)
4. **R Class Transitivity** — `android.nonTransitiveRClass=true` in `gradle.properties`
5. **Build Performance** — `org.gradle.caching=true`, `org.gradle.parallel=true`, configuration cache, JVM args optimized
6. **Dependency Verification** — `gradle/verification-metadata.xml` with SHA-256/PGP
7. **Version Recency** — AGP, Gradle wrapper, Kotlin, Compose BOM versions up to date

## How to Run

```
/android build [path]
```

## Process

1. Run `scripts/analyze_gradle.py` for build config
2. Run `scripts/analyze_dependencies.py` for dependency health
3. Check `gradle.properties` for build performance flags
4. Verify `gradle/verification-metadata.xml` existence
5. Check for `build-logic/` convention plugins

## Scoring

| Factor | Weight |
|--------|--------|
| Version catalogs | 20% |
| Convention plugins | 15% |
| KSP over KAPT | 15% |
| R class transitivity | 10% |
| Build performance | 15% |
| Dependency verification | 15% |
| Version recency | 10% |

## Key Flags in gradle.properties

```properties
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.configureondemand=true
android.nonTransitiveRClass=true
android.enableR8.fullMode=true
org.gradle.jvmargs=-Xmx6g -XX:+HeapDumpOnOutOfMemoryError -XX:+UseParallelGC
```
