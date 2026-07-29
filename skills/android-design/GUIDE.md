---
name: android-design
description: >
  Design system implementation audit for Android projects. Evaluates Material 3
  adoption, theme structure, dynamic color, adaptive layout hooks, and token usage
  from source evidence. Triggers on: "design review", "material design",
  "dynamic color", "UI review".
user-invokable: true
argument-hint: "[path]"
---

# Android Design System Implementation Audit

## Static-Only Scope

This skill can score only what source evidence can support:

1. Material 2 vs Material 3 dependencies and component imports
2. Theme structure and color role usage
3. Dynamic color with fallback
4. Window size class and adaptive-layout hooks
5. Typography token usage

## Out of Scope Without Visual Artifacts

- visual hierarchy
- spacing rhythm
- motion quality
- perceived polish
- contrast validation from real rendered colors

Treat Material 3 Expressive as optional or app-type-specific, not a universal penalty.
