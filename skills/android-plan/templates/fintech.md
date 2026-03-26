# Fintech App Improvement Plan

## Priority Areas
- **Security**: Highest priority — encryption, auth, tamper detection
- **Performance**: Transaction speed, real-time balance updates
- **Compliance**: Data protection, audit logging

## Phase 1: Foundation (Weeks 1-2)
- Fix ALL security findings (Critical AND High)
- StrongBox-backed Keystore for encryption keys
- Biometric auth with CryptoObject (per-operation, not time-based)
- Network security config: cert pinning + Certificate Transparency
- R8 with custom obfuscation dictionaries
- Disable WebView file access, JavaScript (unless required)

## Phase 2: Modernization (Weeks 3-8)
- Credential Manager for passkey-based auth
- Play Integrity API (standard requests for balance, classic for transfers)
- Room + SQLCipher for local transaction history
- DataStore + Tink for sensitive preferences
- Compose for dashboard, transaction list, transfer screens

## Phase 3: Optimization (Weeks 9-16)
- Baseline Profile covering login → dashboard → transfer flow
- Accessibility: amount readout, transaction descriptions, form labels
- Supply chain: Gradle verification-metadata.xml with PGP
- StrictMode + LeakCanary (no sensitive data in heap dumps)
- Certificate Transparency enforcement (API 36+)

## Phase 4: Excellence (Months 5-6)
- Adaptive layouts for tablet banking (list-detail canonical layout)
- Screenshot tests for balance states, error states, empty states
- Root/tamper detection with Play Integrity device verdicts
- Predictive back with secure session handling
- Runtime integrity checks and anti-debugging measures
