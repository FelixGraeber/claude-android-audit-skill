# Material Design 3 -- Component Selection & Design Rules

## Color System

### Color Roles

| Role | Purpose | Typical Usage |
|------|---------|---------------|
| Primary | Key brand color | FAB, prominent buttons, active states |
| On Primary | Content on primary | Text/icons on primary surfaces |
| Primary Container | Standout fill | Cards, chips with emphasis |
| Secondary | Supporting color | Less prominent components, filters |
| Tertiary | Accent/complement | Contrast accents, highlighting |
| Surface | Background areas | Scaffolds, cards, sheets |
| Surface Container (Low/High/Highest) | Layered surfaces | Elevated cards, nav rail, dialogs |
| Error | Error states | Validation, destructive actions |
| Outline | Borders | Text fields, dividers |
| Outline Variant | Subtle borders | Cards, subtle separation |

### Dynamic Color (Android 12+)

```kotlin
// Compose
val colorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    if (isSystemInDarkTheme()) dynamicDarkColorScheme(context)
    else dynamicLightColorScheme(context)
} else {
    if (isSystemInDarkTheme()) darkColorScheme()
    else lightColorScheme()
}

MaterialTheme(colorScheme = colorScheme) { ... }
```

### Contrast Requirements

- Normal text: 4.5:1 minimum contrast ratio (WCAG AA)
- Large text (>=14sp bold or >=18sp): 3:1 minimum
- UI components and graphical objects: 3:1 minimum
- M3 scheme is designed to meet these when using on-color roles correctly
- Always pair: primary with onPrimary, surface with onSurface, etc.

---

## Typography

### 15 Type Roles

| Category | Sizes | Typical Usage |
|----------|-------|---------------|
| Display | L (57sp), M (45sp), S (36sp) | Hero text, large numbers |
| Headline | L (32sp), M (28sp), S (24sp) | Screen titles, section headers |
| Title | L (22sp), M (16sp medium), S (14sp medium) | Card titles, dialog titles |
| Body | L (16sp), M (14sp), S (12sp) | Paragraph text, descriptions |
| Label | L (14sp medium), M (12sp medium), S (11sp medium) | Buttons, chips, nav labels, captions |

### Rules

- Always use `sp` (scale-independent pixels) for text sizes -- never `dp` for text
- Respect user font scaling up to 200%
- Limit to 2-3 type roles per screen for visual hierarchy
- Display: 1 per screen max. Headline: 1-2. Body: primary content.

---

## Component Selection Guide

### Buttons

| Component | When to Use |
|-----------|-------------|
| Filled Button | Primary action, 1 per screen area |
| Outlined Button | Secondary/alternative action |
| Text Button | Lowest emphasis, dialogs, inline |
| Elevated Button | Mid-emphasis on flat surfaces |
| Tonal Button | Mid-emphasis, softer than filled |
| FAB | Primary screen action, persistent |
| Extended FAB | Primary action needing label, scrollable screens |
| Small FAB | Secondary quick actions |
| Large FAB | Hero action on large screens |
| Icon Button | Actions with universally understood icons |

### Navigation

| Component | When to Use |
|-----------|-------------|
| NavigationBar (Bottom) | 3-5 top-level destinations, compact screens |
| NavigationRail | Medium screens (600-840dp), tablet/foldable |
| NavigationDrawer | Expanded screens (>840dp), 6+ destinations |
| TopAppBar (Small) | Default, minimal title |
| TopAppBar (Medium) | Title prominence needed |
| TopAppBar (Large) | Maximum title emphasis, long titles |
| CenterAligned TopAppBar | Branded/centered title, no leading nav |
| Tabs | Parallel content at same hierarchy level |
| BottomSheet | Secondary content/actions without leaving context |

### Containers & Surfaces

| Component | When to Use |
|-----------|-------------|
| Card (Elevated) | Grouped content, browsable collections |
| Card (Filled) | Content on surface background, less emphasis |
| Card (Outlined) | Content needing clear boundary |
| Dialog | Interrupting decisions, confirmations |
| BottomSheet (Modal) | Non-critical choices, overflowing actions |
| BottomSheet (Standard) | Persistent supplementary content |
| Snackbar | Brief feedback, optional action |
| Banner | Persistent, non-blocking messages |

### Selection & Input

| Component | When to Use |
|-----------|-------------|
| Assist Chip | Smart suggestions, contextual actions |
| Filter Chip | Multi-select filtering |
| Input Chip | User-entered entities (tags, contacts) |
| Suggestion Chip | Dynamically generated suggestions |
| Checkbox | Multiple selection from list |
| Radio Button | Single selection from list |
| Switch | Binary on/off toggle |
| Slider | Value from continuous range |
| Date Picker | Date selection |
| Time Picker | Time selection |
| Search Bar | Full-width search with suggestions |

---

## Window Size Classes

| Class | Breakpoint | Typical Devices |
|-------|-----------|-----------------|
| Compact | width < 600dp | Phones portrait |
| Medium | 600dp <= width < 840dp | Tablets portrait, foldables unfolded |
| Expanded | width >= 840dp | Tablets landscape, desktop |

### Navigation by Size Class

| Size Class | Primary Navigation | Secondary |
|------------|-------------------|-----------|
| Compact | NavigationBar (bottom) | TopAppBar |
| Medium | NavigationRail | TopAppBar |
| Expanded | NavigationDrawer (permanent) | TopAppBar optional |

```kotlin
val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass
val navType = when {
    windowSizeClass.windowWidthSizeClass == WindowWidthSizeClass.EXPANDED ->
        NavigationType.PERMANENT_DRAWER
    windowSizeClass.windowWidthSizeClass == WindowWidthSizeClass.MEDIUM ->
        NavigationType.RAIL
    else -> NavigationType.BOTTOM_BAR
}
```

---

## Canonical Layouts

### List-Detail

Two panes: list on left, detail on right (expanded); single pane with navigation (compact).

```kotlin
ListDetailPaneScaffold(
    directive = navigator.scaffoldDirective,
    value = navigator.scaffoldValue,
    listPane = { ListContent() },
    detailPane = { DetailContent() }
)
```

### Feed

Staggered or grid content that reflows based on available width.

- Compact: single column
- Medium: 2 columns
- Expanded: 3+ columns

### Supporting Pane

Primary content with collapsible supporting panel.

- Compact: supporting content in bottom sheet
- Medium: supporting content in side sheet (30-40% width)
- Expanded: persistent side panel

---

## M3 Expressive

### Intensity Levels

| Level | Description | When to Use |
|-------|-------------|-------------|
| Foundational | Standard M3, clean and functional | Productivity apps, enterprise tools |
| Excellent | Selective expressiveness, 1-2 hero moments | Consumer apps, content apps |
| Transformative | Bold expression throughout | Entertainment, creative, social apps |

### Principles

- **Max 1-2 hero moments per screen** -- not everything should compete for attention
- **Shape contrast:** Mix rounded and angular shapes to create hierarchy (e.g., rounded FAB on angular cards)
- **Rich color:** Use tertiary and custom colors beyond primary/secondary for visual richness
- **Type hierarchy:** Use Display/Headline sizes boldly for hero content; contrast with subtle Body text
- **Motion:** Shape morph transitions between states (e.g., FAB morphing into a sheet); spring-based physics for natural feel
- **Emphasis through contrast:** The hero element should differ from surrounding elements in at least 2 properties (color, shape, size, motion)

### Shape System

| Shape | Usage |
|-------|-------|
| None (0dp) | Sharp, angular -- toolbars, full-width containers |
| Extra Small (4dp) | Subtle rounding -- text fields, chips |
| Small (8dp) | Cards, snackbars |
| Medium (12dp) | Dialogs, navigation drawers |
| Large (16dp) | Sheets, FAB |
| Extra Large (28dp) | Large sheets, hero cards |
| Full (50%) | Circular -- icon buttons, avatar images |
