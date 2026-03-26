# OWASP Mobile Top 10 (2024) -- Android Audit Reference

## M1: Improper Credential Usage

**Description:** Hardcoded credentials, API keys, or tokens in source code or configuration files. Improper storage of user credentials in plaintext or weakly protected storage.

**Android File Patterns:**
- `*.kt`, `*.java` -- hardcoded strings
- `res/values/strings.xml` -- API keys in resources
- `local.properties`, `gradle.properties` -- leaked secrets
- `BuildConfig` fields -- keys compiled into APK
- `assets/` -- config files with credentials

**Code Patterns to Grep:**

```
rg -i "(api[_-]?key|secret|password|token|credential)\s*=\s*\"[^\"]+\"" --type kotlin --type java
rg "buildConfigField.*\".*key\|secret\|token\|password" --glob "*.gradle*"
rg -i "Bearer\s+[A-Za-z0-9\-._~+/]+" --type kotlin --type java
rg "-----BEGIN (RSA |EC )?PRIVATE KEY" -r
```

**Audit Checklist:**
- [ ] No hardcoded API keys, secrets, or passwords in source
- [ ] Credentials stored in Android Keystore, not SharedPreferences
- [ ] BuildConfig secrets injected from CI/CD, not committed
- [ ] `.gitignore` includes `local.properties`, `*.jks`, `*.keystore`
- [ ] No credentials in logcat output (check `Log.d/Log.v` calls)

---

## M2: Inadequate Supply Chain Security

**Description:** Use of unverified or compromised dependencies, malicious SDKs, lack of dependency verification.

**Android File Patterns:**
- `build.gradle.kts` / `build.gradle` -- dependency declarations
- `libs.versions.toml` -- version catalog
- `gradle/verification-metadata.xml` -- dependency verification
- `gradle.lockfile` -- dependency locking

**Code Patterns to Grep:**

```
rg "implementation|api|compileOnly" --glob "*.gradle*" --glob "*.toml"
rg "maven\s*\{" --glob "*.gradle*"  # custom/untrusted repos
rg "jitpack" --glob "*.gradle*"     # jitpack repos (unsigned)
```

**Audit Checklist:**
- [ ] Dependency verification enabled (`gradle/verification-metadata.xml`)
- [ ] No `jitpack.io` dependencies in production (unsigned, mutable)
- [ ] Dependencies from Maven Central or Google Maven only
- [ ] Dependabot or Renovate configured for automated updates
- [ ] No wildcard version ranges (`+`, `latest`, `SNAPSHOT`)
- [ ] SDK impact analysis performed (permissions, data collection)
- [ ] License compatibility verified for all dependencies

---

## M3: Insecure Authentication/Authorization

**Description:** Weak biometric implementation, missing server-side auth validation, improper session management.

**Android File Patterns:**
- `*Auth*.kt`, `*Login*.kt`, `*Session*.kt`
- `AndroidManifest.xml` -- permission declarations
- Network layer files -- token handling

**Code Patterns to Grep:**

```
rg "BiometricPrompt" --type kotlin
rg "BIOMETRIC_WEAK" --type kotlin     # should use BIOMETRIC_STRONG
rg "setDeviceCredentialAllowed" --type kotlin  # deprecated
rg "SharedPreferences.*token\|session" --type kotlin
rg "allowBackup.*true" --glob "AndroidManifest.xml"
```

**Audit Checklist:**
- [ ] BiometricPrompt uses `BIOMETRIC_STRONG` (Class 3), not `BIOMETRIC_WEAK`
- [ ] Authentication tokens stored in EncryptedSharedPreferences or Keystore
- [ ] Server validates all auth tokens (not client-only validation)
- [ ] Session expiry and refresh token rotation implemented
- [ ] `android:allowBackup="false"` or backup rules exclude auth data
- [ ] No auth bypass through exported Activities (deep links checked)
- [ ] Rate limiting on authentication endpoints

---

## M4: Insufficient Input/Output Validation

**Description:** SQL injection, XSS in WebViews, path traversal, intent injection.

**Android File Patterns:**
- `*WebView*.kt` -- WebView configurations
- `*Provider*.kt` -- ContentProvider queries
- `*Dao*.kt` -- Room/SQLite queries
- Deep link handlers

**Code Patterns to Grep:**

```
rg "setJavaScriptEnabled\(true\)" --type kotlin
rg "addJavascriptInterface" --type kotlin
rg "rawQuery|execSQL" --type kotlin       # raw SQL (injection risk)
rg "evaluateJavascript" --type kotlin
rg "loadUrl.*javascript:" --type kotlin
rg "intent\.data\b" --type kotlin         # unvalidated deep link data
rg "setAllowFileAccess\(true\)" --type kotlin
```

**Audit Checklist:**
- [ ] WebView JavaScript disabled unless required; if enabled, interface methods annotated `@JavascriptInterface`
- [ ] WebView `setAllowFileAccess(false)`, `setAllowContentAccess(false)`
- [ ] Room DAO uses parameterized `@Query`, no `@RawQuery` with user input
- [ ] ContentProvider `query()` uses parameterized selection args
- [ ] Deep link parameters validated and sanitized before use
- [ ] File paths validated against path traversal (`../`)
- [ ] Intent extras validated before casting/use

---

## M5: Insecure Communication

**Description:** Cleartext traffic, missing certificate pinning, weak TLS configuration, trusting all certificates.

**Android File Patterns:**
- `res/xml/network_security_config.xml`
- `AndroidManifest.xml` -- `usesCleartextTraffic`
- OkHttp/Retrofit configuration files
- Custom `TrustManager` / `SSLSocketFactory`

**Code Patterns to Grep:**

```
rg "usesCleartextTraffic.*true" --glob "*.xml"
rg "cleartextTrafficPermitted.*true" --glob "*.xml"
rg "TrustAllCerts\|ALLOW_ALL\|trustAllCertificates\|X509TrustManager" --type kotlin --type java
rg "hostnameVerifier.*ALLOW_ALL\|HostnameVerifier\s*\{.*true" --type kotlin
rg "http://" --type kotlin --type java     # non-HTTPS URLs
rg "SSLSocketFactory\|TrustManager" --type kotlin
rg "onReceivedSslError.*proceed" --type kotlin  # WebView SSL bypass
```

**Audit Checklist:**
- [ ] `network_security_config.xml` exists and is referenced in manifest
- [ ] `cleartextTrafficPermitted="false"` for all domains (or globally)
- [ ] Certificate pinning configured for API domains (pin backup included)
- [ ] No custom `TrustManager` that trusts all certificates
- [ ] No `HostnameVerifier` that accepts all hostnames
- [ ] WebView `onReceivedSslError` calls `handler.cancel()`, never `proceed()`
- [ ] TLS 1.2+ enforced (TLS 1.0/1.1 disabled)
- [ ] No HTTP URLs in production code

---

## M6: Inadequate Privacy Controls

**Description:** PII leakage, excessive data collection, missing data deletion, lack of consent.

**Android File Patterns:**
- `AndroidManifest.xml` -- permissions
- Analytics/tracking SDK configurations
- Logging files
- Data layer / repository files

**Code Patterns to Grep:**

```
rg "ACCESS_FINE_LOCATION\|ACCESS_COARSE_LOCATION\|READ_CONTACTS\|READ_CALENDAR\|CAMERA\|RECORD_AUDIO" --glob "AndroidManifest.xml"
rg "Log\.(d|v|i|w|e)\(" --type kotlin   # logging PII
rg "Firebase\.analytics\|Amplitude\|Mixpanel\|Adjust" --type kotlin
rg "advertisingId\|getAdvertisingIdInfo" --type kotlin
rg "IMEI\|getDeviceId\|getSubscriberId" --type kotlin
```

**Audit Checklist:**
- [ ] Only necessary permissions declared (no over-requesting)
- [ ] PII not written to logcat (especially in release builds)
- [ ] Analytics anonymize user data, no PII in event properties
- [ ] Data deletion API/endpoint available for user account deletion
- [ ] Data safety form accurately reflects data collection
- [ ] Advertising ID usage complies with policy (not linked to PII)
- [ ] Clipboard access not reading sensitive data without user action

---

## M7: Insufficient Binary Protections

**Description:** No code obfuscation, debuggable release builds, lack of tamper detection.

**Android File Patterns:**
- `build.gradle.kts` -- release config
- `proguard-rules.pro` / `r8-rules.pro`
- `AndroidManifest.xml` -- debuggable flag

**Code Patterns to Grep:**

```
rg "minifyEnabled\s*(=\s*)?false" --glob "*.gradle*"
rg "debuggable\s*(=\s*)?true" --glob "*.gradle*" --glob "*.xml"
rg "isDebuggable" --type kotlin
rg "proguardFiles" --glob "*.gradle*"
rg "shrinkResources\s*(=\s*)?false" --glob "*.gradle*"
```

**Audit Checklist:**
- [ ] `minifyEnabled = true` for release build type
- [ ] `shrinkResources = true` for release build type
- [ ] R8 full mode enabled (`android.enableR8.fullMode=true`)
- [ ] `android:debuggable` not set (defaults to false for release)
- [ ] ProGuard/R8 rules don't over-keep (e.g., `-dontshrink`, `-dontobfuscate`)
- [ ] Root/emulator detection for sensitive apps (banking, payments)
- [ ] Play Integrity API integrated for tamper detection

---

## M8: Security Misconfiguration

**Description:** Exported components without protection, debug flags in production, backup exposing sensitive data.

**Android File Patterns:**
- `AndroidManifest.xml` -- all component declarations
- `res/xml/backup_rules.xml`
- `res/xml/data_extraction_rules.xml`

**Code Patterns to Grep:**

```
rg "exported=\"true\"" --glob "AndroidManifest.xml"
rg "android:permission=" --glob "AndroidManifest.xml"
rg "allowBackup.*true" --glob "AndroidManifest.xml"
rg "android:debuggable" --glob "AndroidManifest.xml"
rg "StrictMode" --type kotlin   # should exist in debug
rg "grantUriPermission" --glob "AndroidManifest.xml"
```

**Audit Checklist:**
- [ ] Every `exported="true"` component has `<intent-filter>` or `android:permission`
- [ ] `android:allowBackup="false"` or backup rules exclude sensitive data
- [ ] `dataExtractionRules` configured for Android 12+ (API 31+)
- [ ] No `android:debuggable="true"` in release manifest
- [ ] ContentProviders use `android:permission` or `grantUriPermissions` carefully
- [ ] FileProvider paths don't expose root or sensitive directories
- [ ] `android:taskAffinity` not set to empty (task hijacking risk)

---

## M9: Insecure Data Storage

**Description:** Unencrypted SharedPreferences, world-readable files, sensitive data in external storage.

**Android File Patterns:**
- SharedPreferences usage files
- Database files / Room configuration
- File I/O operations
- Cache directories

**Code Patterns to Grep:**

```
rg "getSharedPreferences\|PreferenceManager" --type kotlin
rg "MODE_WORLD_READABLE\|MODE_WORLD_WRITEABLE" --type kotlin
rg "getExternalStorage\|getExternalFilesDir\|Environment\.getExternal" --type kotlin
rg "openFileOutput\|FileOutputStream" --type kotlin
rg "SQLiteDatabase\.openOrCreate" --type kotlin
rg "Room\.databaseBuilder" --type kotlin
```

**Audit Checklist:**
- [ ] Sensitive data uses EncryptedSharedPreferences or Android Keystore
- [ ] No `MODE_WORLD_READABLE` or `MODE_WORLD_WRITEABLE`
- [ ] Databases encrypted with SQLCipher or similar for sensitive data
- [ ] Sensitive data not stored on external storage
- [ ] Cache cleared of sensitive data on logout
- [ ] No sensitive data in WebView cache (`setCacheMode`)
- [ ] Temporary files deleted after use

---

## M10: Insufficient Cryptography

**Description:** Weak algorithms, poor RNG, hardcoded encryption keys, improper IV/nonce management.

**Android File Patterns:**
- Crypto utility files
- Key generation / storage files
- Any file importing `javax.crypto` or `java.security`

**Code Patterns to Grep:**

```
rg "DES\b|3DES|RC4|MD5|SHA-1(?!-)" --type kotlin --type java
rg "ECB" --type kotlin --type java          # ECB mode (insecure)
rg "SecretKeySpec\(.*\.toByteArray" --type kotlin  # hardcoded key
rg "IvParameterSpec\(.*ByteArray\(" --type kotlin  # static IV
rg "SecureRandom" --type kotlin              # verify proper usage
rg "Cipher\.getInstance" --type kotlin
rg "KeyGenerator\|KeyPairGenerator" --type kotlin
```

**Audit Checklist:**
- [ ] AES-256-GCM or AES-256-CBC with HMAC used (no DES, 3DES, RC4)
- [ ] RSA key size >= 2048 bits, ECDSA >= 256 bits
- [ ] No ECB mode (use GCM or CBC with random IV)
- [ ] IVs/nonces generated with `SecureRandom`, never reused
- [ ] Keys stored in Android Keystore, not hardcoded or in SharedPreferences
- [ ] `SecureRandom` used instead of `Random` for crypto operations
- [ ] SHA-256+ for hashing (no MD5, no SHA-1 for security purposes)
- [ ] No custom crypto implementations (use AndroidX Security or Tink)
