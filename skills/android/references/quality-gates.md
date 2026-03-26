# Quality Gates -- Hard Rules

Agents must NEVER approve or pass a review if any Critical gate is violated. High gates should be flagged prominently. Medium gates are recommendations.

## Critical Severity

These are blocking. Any violation fails the audit.

| # | Rule | What to Check | Why Critical |
|---|------|---------------|--------------|
| C1 | Exported component without permission or intent-filter | `rg 'exported="true"' AndroidManifest.xml` then verify each has `<intent-filter>` or `android:permission` | Arbitrary app can launch your Activity/Service/Receiver, data theft or privilege escalation |
| C2 | usesCleartextTraffic="true" without network security config | `rg 'usesCleartextTraffic' AndroidManifest.xml` and check `res/xml/network_security_config.xml` exists | All traffic unencrypted, MITM attacks, credential sniffing |
| C3 | targetSdk below Play Store requirement (< 35) | Check `targetSdkVersion` in `build.gradle.kts` | App will be rejected from Play Store |
| C4 | Hardcoded secrets in source | `rg -i '(api[_-]?key\|secret\|password\|token)\s*=\s*"[^"]+"' --type kotlin --type java` | Secrets extractable from APK, account compromise |
| C5 | Crash rate >= 1.09% | Android Vitals dashboard or CI crash tracking | Play Store bad behavior threshold, visibility penalty |
| C6 | ANR rate >= 0.47% | Android Vitals dashboard or CI ANR tracking | Play Store bad behavior threshold, visibility penalty |
| C7 | minifyEnabled false in release | `rg 'minifyEnabled.*false' --glob '*.gradle*'` in release block | APK not obfuscated, trivially reverse-engineered, larger binary |
| C8 | android:debuggable="true" in release | `rg 'debuggable' AndroidManifest.xml` and `rg 'debuggable.*true' --glob '*.gradle*'` | Attacker can attach debugger, inspect memory, bypass security |

## High Severity

These are strong warnings. Should be fixed before release.

| # | Rule | What to Check | Impact |
|---|------|---------------|--------|
| H1 | KAPT when KSP alternative exists | `rg 'kapt' --glob '*.gradle*'` for Dagger/Hilt/Room/Moshi | 2-4x slower builds, blocks K2 compiler migration |
| H2 | No Baseline Profile | Check for `baseline-prof.txt` or `baselineprofile` module | 30-50% slower cold start without precompiled critical paths |
| H3 | Touch targets < 48dp | Audit all clickable Composables and XML buttons for sizing | Accessibility failure, unusable for motor-impaired users |
| H4 | EncryptedSharedPreferences usage | `rg 'EncryptedSharedPreferences' --type kotlin` | Deprecated; use DataStore with Tink encryption or Keystore directly |
| H5 | No edge-to-edge implementation | `rg 'enableEdgeToEdge\|WindowCompat.setDecorFitsSystemWindows' --type kotlin` | Mandatory on API 36, content clipped behind system bars |
| H6 | No network_security_config.xml | Check `res/xml/network_security_config.xml` exists | No certificate pinning, no cleartext control, weaker transport security |
| H7 | SSL errors ignored in WebView | `rg 'onReceivedSslError' --type kotlin` then check for `proceed()` | MITM attacks on WebView content, credential theft |
| H8 | onBackPressed() override without OnBackInvokedCallback | `rg 'onBackPressed' --type kotlin` without corresponding `OnBackInvokedCallback` | Broken back navigation on API 36, predictive back animation broken |

## Medium Severity

Recommendations for improved quality.

| # | Rule | What to Check | Impact |
|---|------|---------------|--------|
| M1 | No version catalog (libs.versions.toml) | Check `gradle/libs.versions.toml` exists | Inconsistent dependency versions across modules, harder maintenance |
| M2 | No convention plugins | Check `build-logic/` or `buildSrc/` for shared build config | Duplicated build configuration, drift between modules |
| M3 | Missing StrictMode in debug | `rg 'StrictMode' --type kotlin` | Disk/network on main thread issues go undetected during development |
| M4 | No LeakCanary in debug deps | `rg 'leakcanary' --glob '*.gradle*' --glob '*.toml'` | Memory leaks go undetected, OOM crashes in production |
| M5 | collectAsState instead of collectAsStateWithLifecycle | `rg 'collectAsState[^W]' --type kotlin` (matches collectAsState but not collectAsStateWithLifecycle) | Flow collection continues when app backgrounded, wasted resources, potential crashes |
| M6 | No screenshot tests | Check for Roborazzi, Paparazzi, or Compose Preview Screenshot Testing setup | Visual regressions go undetected, manual QA burden |

## Gate Enforcement

### During Code Review
- **Critical:** Block merge. Must fix before approval.
- **High:** Request changes. Can merge with tech debt ticket if justified.
- **Medium:** Comment. Merge allowed, track for improvement.

### During Audit
- **Critical violations:** Score capped at 40/100 regardless of other scores.
- **3+ High violations:** Score capped at 60/100.
- **Any Critical violation in security category:** Security score = 0.
