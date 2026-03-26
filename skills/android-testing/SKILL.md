---
name: android-testing
description: >
  Testing strategy assessment for Android projects. Evaluates Compose testing,
  screenshot testing, Robolectric usage, test balance, coverage, and CI/CD
  maturity. Triggers on: "testing", "test coverage", "screenshot test",
  "CI/CD", "compose test".
user-invokable: true
argument-hint: "[path]"
---

# Android Testing Assessment

Evaluate testing strategy, coverage, and CI/CD maturity.

## What This Checks

1. **Compose Testing** — `ComposeTestRule` usage, semantic matchers (`onNodeWithText`, `onNodeWithContentDescription`), `testTag` coverage
2. **Screenshot Testing** — Roborazzi, Paparazzi, or Compose Preview Screenshot Testing configured
3. **Robolectric** — JVM-based Android testing for faster iteration
4. **Test Strategy Balance** — Unit tests (JUnit + Mockk/Turbine), UI tests (ComposeTestRule), screenshot tests, integration tests, instrumented tests (10% max)
5. **Test Coverage** — Test file count relative to source, critical paths covered
6. **CI/CD** — Build caching (`org.gradle.caching=true`), test sharding, parallel execution, Gradle Test Retry Plugin

## How to Run

```
/android testing [path]
```

## Process

1. Count test files in `test/` and `androidTest/` directories
2. Grep for testing patterns (ComposeTestRule, @Test, Roborazzi, Paparazzi)
3. Check build.gradle.kts for test dependencies
4. Scan CI config files (.github/workflows/, Jenkinsfile, bitrise.yml)
5. Check gradle.properties for build optimization flags

## Scoring

| Factor | Weight |
|--------|--------|
| Compose testing | 20% |
| Test balance | 20% |
| Screenshot testing | 15% |
| Coverage ratio | 15% |
| CI/CD maturity | 15% |
| Robolectric usage | 15% |

## Recommended Test Strategy

| Layer | Tool | Target |
|-------|------|--------|
| Unit tests | JUnit + Mockk/Turbine | Business logic, ViewModels |
| Compose UI tests | ComposeTestRule + Robolectric | Component behavior |
| Screenshot tests | Roborazzi/Paparazzi | Visual regression |
| Integration tests | Robolectric | Feature flows |
| Instrumented tests | Espresso/UiAutomator | Real device (10%) |
