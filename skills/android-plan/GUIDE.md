---
name: android-plan
description: >
  Strategic Android improvement roadmap. 4-phase plan with app-type specific
  templates for social, ecommerce, fintech, health/fitness, productivity apps.
  Triggers on: "android plan", "android strategy", "android roadmap",
  "improvement plan".
user-invokable: true
argument-hint: "[app-type]"
---

# Android Strategic Plan

Generate a 4-phase improvement roadmap tailored to your app type.

## How to Run

```
/android plan [app-type]
```

App types: `social`, `ecommerce`, `fintech`, `health-fitness`, `productivity`, `generic`

## Process

1. If path provided, scan project to auto-detect app type
2. Load app-type template from `templates/`
3. If audit data available, prioritize based on findings
4. Generate 4-phase roadmap

## 4-Phase Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Fix all Critical severity issues
- Set up Baseline Profiles
- Fix security vulnerabilities
- Ensure targetSdk meets Play Store deadline

### Phase 2: Modernization (Weeks 3-8)
- Compose migration for new screens
- Architecture alignment (UDF, DI, Repository)
- Testing setup (ComposeTestRule, screenshot tests)
- Edge-to-edge implementation

### Phase 3: Optimization (Weeks 9-16)
- Performance tuning (R8 full mode, startup optimization)
- Accessibility audit and fixes
- Android 16 compatibility
- CI/CD maturity (build caching, test sharding)

### Phase 4: Excellence (Months 5-6)
- Material 3 Expressive adoption
- Full screenshot test coverage
- Convention plugins and version catalogs
- Dependency verification
- Play Integrity API integration

## Templates

Each template in `templates/` provides app-type specific priorities and benchmarks.
