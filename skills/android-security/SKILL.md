---
name: android-security
description: >
  Security audit for Android projects. Checks OWASP-oriented client-side risks,
  manifest exposure, hardcoded secrets, WebView handling, storage posture, and
  build obfuscation evidence. Triggers on: "security", "OWASP", "permissions",
  "encryption", "WebView", "certificate pinning".
---

# Android Security Audit

## Scope

This skill scores only what can be defended from static Android project evidence.

It should separate:

- verified static findings
- likely risks from static evidence
- backend, operational, and runtime controls that require external evidence

## Storage Guidance

Use one repo-wide position:

- `androidx.security:security-crypto` is deprecated and should be treated as migration debt.
- Do not prescribe a single replacement for every app.
- Prefer threat-model-specific guidance:
  - consumer app: platform keystore + minimal secret storage
  - higher-risk app: keystore-backed key handling plus stronger architectural separation
  - SDK/library: avoid forcing storage strategy assumptions on host apps

## Avoid Overclaiming

- Play Integrity is contextual, not a universal maturity requirement.
- Certificate pinning is situational and must include operational tradeoffs.
- Static source review cannot prove server-side controls, incident response, or compliance posture.
