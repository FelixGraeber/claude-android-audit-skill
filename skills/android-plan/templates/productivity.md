# Productivity App Improvement Plan

## Priority Areas
- **Architecture**: Multi-module, offline-first, data sync
- **Large screens**: Tablet and foldable support critical
- **Performance**: Fast startup, smooth editing

## Phase 1: Foundation (Weeks 1-2)
- Fix Critical findings from audit
- Baseline Profile for app startup and primary workflow
- Edge-to-edge with keyboard (IME) insets for editing
- R8 minification and resource shrinking

## Phase 2: Modernization (Weeks 3-8)
- Compose for editor, list, and settings screens
- Offline-first architecture: Room + WorkManager sync
- Type-safe Navigation 2.8+ for deep linking support
- Repository pattern for documents/tasks/notes
- Hilt DI across modules

## Phase 3: Optimization (Weeks 9-16)
- WindowSizeClass: list-detail layout for medium/expanded screens
- NavigationRail for medium, NavigationDrawer for expanded
- Predictive back with document save confirmation
- Compose stability for document models
- Accessibility: heading structure, form labels, keyboard navigation
- KSP migration, version catalogs, convention plugins

## Phase 4: Excellence (Months 5-6)
- Foldable support: table-top mode for reference + editing
- App Shortcuts for quick actions
- Widget with Glance API (dynamic color)
- Screenshot tests across all WindowSizeClasses
- KMP: share document parsing logic with iOS
- Per-app language preferences
