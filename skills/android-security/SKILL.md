---
name: android-security
description: >
  Security audit for Android projects. Checks OWASP Mobile Top 10 (2024),
  network security config, cryptography, component security, WebView hardening,
  R8 obfuscation, supply chain integrity, and Play Integrity API. Triggers on:
  "security", "OWASP", "permissions", "encryption", "WebView", "certificate pinning".
user-invokable: true
argument-hint: "[path]"
---

# Android Security Audit

Comprehensive security posture assessment based on OWASP Mobile Top 10 (2024).

## What This Checks

1. **Network Security** — `network_security_config.xml` exists, cleartext disabled, certificate pinning, Certificate Transparency (API 36+)
2. **Data Storage** — No plain SharedPreferences for secrets, DataStore + Tink preferred, no EncryptedSharedPreferences (deprecated), SQLCipher for sensitive Room DBs
3. **Cryptography** — Android Keystore usage, StrongBox, AES-256-GCM, no weak algos (DES/MD5/SHA1/ECB), SecureRandom not java.util.Random, no hardcoded keys/IVs
4. **Component Security** — `android:exported` explicit on all components, exported components have permissions, no implicit service binding, FileProvider used, PendingIntent.FLAG_IMMUTABLE
5. **WebView Hardening** — JavaScript disabled by default, no file:// access, WebViewAssetLoader, SSL errors never ignored, Safe Browsing enabled, MIXED_CONTENT_NEVER_ALLOW
6. **R8 Obfuscation** — minifyEnabled, no `-dontobfuscate`, no overly broad `-keep`, mapping.txt saved
7. **Supply Chain** — `gradle/verification-metadata.xml` with SHA-256/PGP, Dependabot/similar enabled
8. **Secrets Detection** — No API keys, tokens, passwords hardcoded in source
9. **Play Integrity** — Integration for sensitive server operations, server-side verification

## How to Run

```
/android security [path]
```

## Process

1. Run `scripts/analyze_manifest.py` for permissions and component analysis
2. Grep source for hardcoded secrets patterns
3. Parse `network_security_config.xml` if present
4. Run `scripts/check_r8_config.py`
5. Check for `verification-metadata.xml`
6. Analyze crypto patterns in source

## Scoring

| Factor | Weight |
|--------|--------|
| Network security | 15% |
| Data storage | 15% |
| Cryptography | 15% |
| Component security | 15% |
| WebView | 10% |
| R8 obfuscation | 10% |
| Supply chain | 10% |
| Play Integrity | 10% |

## Critical Findings (always flag)

- Hardcoded API keys/tokens/passwords in source → Critical
- `usesCleartextTraffic="true"` without network security config → Critical
- Exported component without permission → Critical
- SSL errors ignored (`handler.proceed()`) in WebView → Critical
- `android:debuggable="true"` in release → Critical

## Reference

Load on-demand: `references/owasp-mobile-2024.md`
