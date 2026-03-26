---
name: android-accessibility
description: >
  Accessibility audit for Android projects. Checks touch targets (48dp),
  content descriptions, TalkBack support, focus management, Compose semantics,
  color contrast, and heading annotations. Triggers on: "accessibility",
  "a11y", "TalkBack", "content description", "touch target".
user-invokable: true
argument-hint: "[path]"
---

# Android Accessibility Audit

Evaluate accessibility compliance for inclusive app experiences.

## What This Checks

1. **Touch Targets** — Interactive elements >= 48dp x 48dp, `Modifier.minimumInteractiveComponentSize()` usage
2. **Content Descriptions** — All `Icon`/`Image`/`ImageButton` have `contentDescription`, decorative elements set `null`
3. **Compose Semantics** — `Modifier.semantics`, `mergeDescendants`, roles (`Role.Button`, `Role.Checkbox`), state descriptions, click labels
4. **Color Contrast** — `MaterialTheme.colorScheme` roles used (not hardcoded), 4.5:1 text contrast, 3:1 non-text
5. **Focus Management** — Logical traversal order, `screenReaderFocusable`, `focusRequester` usage
6. **Headings** — `heading()` semantics for section titles, enabling TalkBack heading navigation
7. **Live Regions** — `accessibilityLiveRegion` for dynamic content updates
8. **Custom Actions** — `customActions` in semantics for complex gestures

## How to Run

```
/android accessibility [path]
```

## Process

1. Run `scripts/analyze_compose.py --mode accessibility`
2. Grep for accessibility patterns in source
3. Check for missing content descriptions
4. Analyze touch target sizes

## Scoring

| Factor | Weight |
|--------|--------|
| Touch targets | 20% |
| Content descriptions | 20% |
| Compose semantics | 20% |
| Color contrast | 15% |
| Focus management | 15% |
| Headings | 10% |

## Key Thresholds

- Touch targets: >= 48dp (Material guideline, always High if violated)
- Text contrast: 4.5:1 minimum (WCAG AA)
- Large text contrast: 3:1 minimum (WCAG AA)
- Non-text contrast: 3:1 minimum
