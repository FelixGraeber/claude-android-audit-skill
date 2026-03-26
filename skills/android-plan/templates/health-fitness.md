# Health & Fitness App Improvement Plan

## Priority Areas
- **Privacy**: Health data protection, granular permissions
- **Performance**: Real-time sensor data, background tracking
- **Android 16**: Granular health permissions migration

## Phase 1: Foundation (Weeks 1-2)
- Migrate BODY_SENSORS to granular permissions (READ_HEART_RATE, etc.)
- Health Connect API integration
- Encrypted storage for health data (Room + SQLCipher)
- Foreground service types: `health`, `location` (with proper permissions)
- Baseline Profile for workout tracking screens

## Phase 2: Modernization (Weeks 3-8)
- Compose for dashboard, workout log, progress charts
- ViewModel + StateFlow for real-time sensor data display
- WorkManager for background sync with health platforms
- Offline-first: local workout storage with cloud sync
- Edge-to-edge with Scaffold for tracking screens

## Phase 3: Optimization (Weeks 9-16)
- Battery optimization: minimal wake locks during tracking
- Compose performance: derivedStateOf for chart updates
- Accessibility: workout descriptions, progress announcements
- Permission rationale flows (health data is sensitive)
- Notification channels: workout reminders vs progress updates

## Phase 4: Excellence (Months 5-6)
- Adaptive layouts: workout details on tablets
- Health Connect FHIR medical records (API 36+)
- Companion device support (RangingManager for wearables)
- Screenshot tests for dashboard states and workout flows
- M3 Expressive: hero moment on progress milestones
