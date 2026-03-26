# Social App Improvement Plan

## Priority Areas
- **Performance**: Feed scrolling, image loading, real-time updates
- **Security**: Auth, message encryption, privacy
- **Accessibility**: Content descriptions on UGC, dynamic content

## Phase 1: Foundation (Weeks 1-2)
- Fix Critical security findings (exported components, cleartext)
- Baseline Profile covering feed scroll and navigation
- Credential Manager migration for auth
- Network security config with cert pinning for API

## Phase 2: Modernization (Weeks 3-8)
- Compose migration for feed, profile, and messaging screens
- LazyColumn with stable keys for feed items
- Coil 3.0 for image loading with memory/disk cache
- Offline-first: Room + sync for feed data
- Edge-to-edge with keyboard (IME) insets for chat

## Phase 3: Optimization (Weeks 9-16)
- derivedStateOf for scroll-dependent UI (FAB visibility, header collapse)
- Compose stability for feed item models (@Immutable data classes)
- Accessibility: content descriptions on images/media, live regions for new messages
- Push notification channels (importance levels for messages vs social)
- WorkManager for background sync (not foreground services)

## Phase 4: Excellence (Months 5-6)
- M3 Expressive: hero moment on profile, rich color on feed
- Predictive back gesture with cross-fade animations
- Screenshot tests for feed states (empty, loading, error, populated)
- Dynamic color with brand color fallback
- Photo picker integration (embedded, API 36+)
