---
name: android-accessibility
description: >
  Accessibility preflight for Android projects. Uses static source evidence to
  flag likely issues in semantics, labels, and touch-target setup while clearly
  separating low-confidence heuristics from verified findings.
user-invokable: true
argument-hint: "[path]"
---

# Android Accessibility Preflight

## Verified Static Signals

1. Missing explicit `contentDescription` on `Icon`, `Image`, or `AsyncImage`
2. Decorative imagery correctly marked with `contentDescription = null`
3. Semantics APIs such as `semantics`, `clearAndSetSemantics`, `heading`, `paneTitle`, and `liveRegion`

## Low-Confidence Heuristics

1. Touch-target risks inferred from clickable modifier chains
2. Missing accessibility structure in Compose-heavy surfaces

## Out of Scope Without Runtime Artifacts

- actual contrast
- TalkBack usability
- focus order
- switch access behavior
- screen-reader announcements in real flows
