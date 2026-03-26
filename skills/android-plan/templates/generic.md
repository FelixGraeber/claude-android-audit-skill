# Generic Android Improvement Plan

## Phase 1: Foundation (Weeks 1-2)
- Fix all Critical findings from audit
- Set targetSdk to meet Play Store deadline
- Enable R8 minification and resource shrinking for release builds
- Add network_security_config.xml with cleartext disabled
- Set android:exported explicitly on all components
- Generate initial Baseline Profile

## Phase 2: Modernization (Weeks 3-8)
- Adopt Jetpack Compose for new screens (keep XML for existing)
- Implement ViewModel + StateFlow UDF pattern
- Set up Hilt or Koin for dependency injection
- Migrate to type-safe Navigation 2.8+ with @Serializable routes
- Implement edge-to-edge with proper WindowInsets handling
- Add Compose UI tests with ComposeTestRule

## Phase 3: Optimization (Weeks 9-16)
- Enable R8 full mode, optimize ProGuard rules
- Add Startup Profile alongside Baseline Profile
- Implement Compose stability annotations (@Stable, @Immutable)
- Add key() to all LazyColumn/LazyRow items
- Integrate LeakCanary for debug builds
- Enable StrictMode in debug builds
- Migrate KAPT to KSP
- Set up Version Catalogs (libs.versions.toml)
- Implement accessibility: 48dp touch targets, content descriptions, semantics

## Phase 4: Excellence (Months 5-6)
- Android 16 compatibility: predictive back, large screen adaptation
- Material 3 Expressive adoption (1-2 hero moments)
- Screenshot testing with Roborazzi
- Convention plugins in build-logic/
- Gradle dependency verification (verification-metadata.xml)
- CI/CD: build caching, test sharding, parallel execution
- Play Integrity API for sensitive operations
