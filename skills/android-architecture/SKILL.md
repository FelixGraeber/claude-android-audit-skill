---
name: android-architecture
description: >
  Architecture assessment for Android projects. Evaluates Jetpack Compose adoption,
  UDF pattern (ViewModel + StateFlow), dependency injection, type-safe navigation,
  repository pattern, and module structure. Triggers on: "architecture", "compose
  adoption", "module structure", "dependency injection".
user-invokable: true
argument-hint: "[path]"
---

# Android Architecture Assessment

Analyze an Android project's architecture patterns and score structural health.

## What This Checks

1. **Compose Adoption** — Ratio of Compose files to XML layouts; new screens in Compose
2. **UDF Pattern** — ViewModel + StateFlow/MutableStateFlow usage; `collectAsStateWithLifecycle`
3. **Dependency Injection** — Hilt (`@HiltViewModel`, `@Inject`, `@AndroidEntryPoint`) or Koin (`koinModule`, `viewModel()`)
4. **Navigation** — Type-safe Navigation 2.8+ with `@Serializable` routes vs legacy string-based
5. **Repository Pattern** — Data layer abstraction; Repository interfaces with implementations
6. **Module Structure** — Feature modules, core modules, UI/domain/data layering
7. **Single-Activity** — One Activity in manifest (or minimal), navigation via Compose/Fragments

## How to Run

```
/android architecture [path]
```

If no path provided, uses current working directory.

## Process

1. Run `scripts/scan_project.py` to discover project structure
2. Grep for architecture patterns in source files
3. Analyze module dependency graph from build files
4. Score each factor and produce findings

## Scoring

| Factor | Weight |
|--------|--------|
| Compose adoption | 20% |
| UDF pattern | 20% |
| Dependency injection | 15% |
| Navigation | 15% |
| Module structure | 15% |
| Repository pattern | 15% |

## Key Patterns to Grep

```
# Compose adoption
@Composable
setContent {

# UDF
: ViewModel()
StateFlow
MutableStateFlow
collectAsStateWithLifecycle

# DI
@HiltViewModel
@AndroidEntryPoint
@Inject
koinModule

# Navigation
@Serializable
NavHost
composable(

# Repository
: Repository
interface.*Repository
```

## Output

Produces findings with severity levels and actionable recommendations for each factor.
