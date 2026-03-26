# Google Play Store Requirements (2025-2026)

## Target SDK Requirements

| Deadline | Requirement | Impact |
|----------|-------------|--------|
| Aug 2025 | `targetSdkVersion >= 35` (Android 15) | New apps and updates rejected below this |
| Aug 2026 (expected) | `targetSdkVersion >= 36` (Android 16) | New apps and updates rejected below this |
| Nov 2025 | Existing apps not updated: hidden from users on newer devices | Apps targeting very old SDKs become invisible |

Apps must also declare `compileSdkVersion >= targetSdkVersion`.

---

## Data Safety Form

Mandatory for all apps. Must accurately declare:

- **Data collected:** What types of data the app collects (name, email, location, etc.)
- **Data shared:** What data is shared with third parties (including SDKs)
- **Data handling:** Encryption in transit, deletion mechanism available
- **Purpose:** Why each data type is collected (app functionality, analytics, advertising)

### Enforcement

- Apps without a completed data safety form are rejected
- False declarations can result in suspension
- Must be updated when data practices change (e.g., adding new SDK)

### SDK Transparency

- Google Play SDK Index lists popular SDKs and their data practices
- Developers are responsible for declaring data collected by all SDKs

---

## Foreground Service Types (Android 14+)

Apps targeting API 34+ must declare `android:foregroundServiceType` in the manifest.

| Type | Permission Required | Use Case |
|------|-------------------|----------|
| `camera` | `FOREGROUND_SERVICE_CAMERA` | Active camera usage |
| `connectedDevice` | `FOREGROUND_SERVICE_CONNECTED_DEVICE` | Bluetooth, USB, companion |
| `dataSync` | `FOREGROUND_SERVICE_DATA_SYNC` | Data transfer operations |
| `health` | `FOREGROUND_SERVICE_HEALTH` | Exercise, vital monitoring |
| `location` | `FOREGROUND_SERVICE_LOCATION` + location permission | Ongoing location tracking |
| `mediaPlayback` | `FOREGROUND_SERVICE_MEDIA_PLAYBACK` | Audio/video playback |
| `mediaProjection` | `FOREGROUND_SERVICE_MEDIA_PROJECTION` | Screen capture/share |
| `microphone` | `FOREGROUND_SERVICE_MICROPHONE` | Active recording |
| `phoneCall` | `FOREGROUND_SERVICE_PHONE_CALL` | Ongoing call management |
| `remoteMessaging` | `FOREGROUND_SERVICE_REMOTE_MESSAGING` | Message relay from other device |
| `shortService` | None | Brief tasks (<3 min, no type needed) |
| `specialUse` | `FOREGROUND_SERVICE_SPECIAL_USE` | Requires Play Store justification |
| `systemExempted` | System apps only | Not available for third-party |
| `mediaProcessing` | `FOREGROUND_SERVICE_MEDIA_PROCESSING` | Media transcoding/encoding |

### Rules

- Must declare type in manifest AND at runtime when starting service
- `dataSync` limited to 6 hours per invocation
- `mediaProcessing` limited to 6 hours per invocation
- Play Store reviews `specialUse` declarations manually

---

## Photo & Video Permissions

### Android 13+ (API 33+)

`READ_EXTERNAL_STORAGE` replaced by granular permissions:

| Permission | Access |
|-----------|--------|
| `READ_MEDIA_IMAGES` | Photos |
| `READ_MEDIA_VIDEO` | Videos |
| `READ_MEDIA_AUDIO` | Audio files |

### Android 14+ (API 34+)

- `READ_MEDIA_VISUAL_USER_SELECTED` -- partial/selected access
- System photo picker preferred (no permission needed)
- Users can grant access to selected photos only

### Play Store Policy

- Must use photo picker when full library access is not essential
- Full `READ_MEDIA_IMAGES`/`READ_MEDIA_VIDEO` requires justification
- Gallery apps and file managers: exempted with declaration

---

## Notification Permission

### Android 13+ (API 33+)

`POST_NOTIFICATIONS` is a runtime permission.

- New installs: notifications are OFF by default
- Upgrades from pre-API 33: temporary grant until user explicitly denies
- Must request permission before posting any notification
- Request at contextually appropriate time (not immediately on launch)

---

## Exact Alarms

### Android 13+ (API 33+)

`SCHEDULE_EXACT_ALARM` is restricted:

- Not granted by default for new installs targeting API 33+
- Must declare in manifest AND user must grant in Settings
- `USE_EXACT_ALARM` auto-granted but only for alarm clock / timer apps
- Play Store reviews `USE_EXACT_ALARM` declarations

### Alternative

Use `WorkManager` with flex windows or `AlarmManager.setAndAllowWhileIdle()` for inexact timing.

---

## Background Location

Stringent requirements for `ACCESS_BACKGROUND_LOCATION`:

1. First request `ACCESS_FINE_LOCATION` or `ACCESS_COARSE_LOCATION`
2. Separately request `ACCESS_BACKGROUND_LOCATION` in a different dialog
3. Play Store requires:
   - In-app disclosure explaining why background location is needed
   - Video demonstration of the feature requiring background location
   - Written justification in Play Console

Apps without valid justification are rejected.

---

## Play Integrity API

Replaces SafetyNet Attestation (fully deprecated, stopped May 2025).

### Standard Request

Returns device integrity verdict:
- `MEETS_DEVICE_INTEGRITY` -- genuine device, passes CTS
- `MEETS_BASIC_INTEGRITY` -- may be rooted but not actively tampered
- `MEETS_STRONG_INTEGRITY` -- hardware-backed attestation
- `MEETS_VIRTUAL_INTEGRITY` -- known emulator (for testing)

### Integration

```kotlin
val integrityManager = IntegrityManagerFactory.create(context)
val request = IntegrityTokenRequest.builder()
    .setNonce(nonce)
    .build()
integrityManager.requestIntegrityToken(request)
    .addOnSuccessListener { response ->
        // Send response.token() to your server for verification
    }
```

### Policy

- Server-side verification required (never trust client-side)
- Must handle degraded verdicts gracefully (don't hard-block)
- Rate limits: 10K standard requests/day free, classic requests available

---

## Age Signals API (Jan 2026+)

Required for gambling, dating, and age-restricted content apps:

- Must integrate Age Signals API to verify user age
- Replaces self-declaration age gates
- Returns age bracket signal (not exact age)
- Required in regulated markets first, expanding globally

---

## App Quality Guidelines

### Crash & ANR Thresholds

| Metric | Bad Behavior Threshold | Impact |
|--------|----------------------|--------|
| User-perceived crash rate | >= 1.09% | Reduced visibility, warnings |
| User-perceived ANR rate | >= 0.47% | Reduced visibility, warnings |

### Consequences

- **Bad behavior:** warning badge in Play Store, reduced search ranking
- **Persistent bad behavior:** further visibility reduction
- **Extreme cases:** app removal from recommendations entirely
- 28-day rolling window for measurement
- Per-device-type thresholds (phone, tablet, watch, auto, TV)

### Quality Signals Affecting Ranking

- Crash rate and ANR rate
- Install retention (uninstalls after install)
- Rating and review sentiment
- Battery and data usage (Android Vitals)
- App startup time
- Permission request patterns (requesting too many permissions hurts ranking)

---

## Additional Policies

### Ads

- Full-screen interstitial ads must be closable after 15 seconds
- Ads must not mimic system notifications or UI
- Apps for children (Designed for Families) have stricter ad rules

### Subscriptions

- Must offer in-app cancellation or link to Play Store subscription management
- Free trial terms must be clear before purchase
- Grace period handling recommended

### Account Deletion

- Apps with account creation must offer in-app account deletion
- Must also offer web-based deletion path
- Data deletion must be complete within 60 days (or explain retention)
