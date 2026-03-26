# E-Commerce App Improvement Plan

## Priority Areas
- **Performance**: Product catalog scroll, checkout speed
- **Security**: Payment processing, PII protection
- **Conversion**: Smooth checkout, quick add-to-cart

## Phase 1: Foundation (Weeks 1-2)
- Fix Critical security (cleartext, exported components, secrets)
- Baseline Profile covering product list scroll and checkout
- Network security config with cert pinning for payment APIs
- Encrypted storage for payment tokens (Keystore + Tink)

## Phase 2: Modernization (Weeks 3-8)
- Compose for product grid, cart, and checkout screens
- LazyVerticalGrid with stable keys for product catalog
- Coil 3.0 for product images with preloading
- Repository pattern for cart/wishlist with Room persistence
- Edge-to-edge with proper insets on all screens

## Phase 3: Optimization (Weeks 9-16)
- R8 full mode for APK size reduction (product images are heavy)
- Compose stability for product models
- Accessibility: product descriptions, price announcements, cart actions
- Biometric authentication for checkout (BiometricPrompt + CryptoObject)
- WorkManager for order sync and inventory updates

## Phase 4: Excellence (Months 5-6)
- Adaptive layouts: product grid columns per WindowSizeClass
- Play Integrity API for fraud prevention
- Screenshot tests for product cards, cart states, checkout flow
- Per-app language preferences for international stores
- Dynamic feature modules for seller/admin tools
