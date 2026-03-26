---
name: android-design
description: >
  UI/UX and Material Design review for Android projects. Evaluates Material
  Design 3, Material 3 Expressive, dynamic color, window size classes,
  edge-to-edge insets, typography, and component selection. Triggers on:
  "design review", "material design", "dynamic color", "UI review".
user-invokable: true
argument-hint: "[path]"
---

# Android Design Review

Evaluate Material Design compliance and UI/UX patterns.

## What This Checks

1. **M3 Adoption** — Material3 library dependency, `MaterialTheme` usage, M3 components (not M2/AppCompat)
2. **Dynamic Color** — `dynamicDarkColorScheme`/`dynamicLightColorScheme` with fallback, no hardcoded hex colors for theme roles
3. **Window Size Classes** — `calculateWindowSizeClass()`, adaptive layouts per Compact/Medium/Expanded
4. **Edge-to-Edge** — `Scaffold` with `innerPadding`, `systemBarsPadding()`, `safeDrawing` insets
5. **Typography** — `sp` units for text (not `dp`), `MaterialTheme.typography` roles, dynamic type support
6. **Component Selection** — Correct component for use case (FAB for primary action only, NavigationBar for 3-5 destinations, NavigationRail for medium screens)
7. **M3 Expressive** — Intensity levels, max 1-2 hero moments per flow, shape contrast, standard nav preserved

## How to Run

```
/android design [path]
```

## Scoring

| Factor | Weight |
|--------|--------|
| M3 adoption | 20% |
| Dynamic color | 15% |
| Window size classes | 15% |
| Edge-to-edge | 15% |
| Typography | 15% |
| Component selection | 10% |
| M3 Expressive | 10% |

## Cross-References

- For detailed M3 Expressive token guidance: `/material-3-expressive`
- For comprehensive Android design patterns: `/android-design-guidelines`

## Key Anti-Patterns

| Anti-Pattern | Correct Approach |
|-------------|-----------------|
| Hardcoded color hex values | Use `MaterialTheme.colorScheme` roles |
| `dp` for text size | Use `sp` units |
| Multiple FABs per screen | One FAB for primary action only |
| Fixed navigation for all screens | Adapt per window size class |
| Removing text labels for "cleaner" look | Keep labels for usability |
