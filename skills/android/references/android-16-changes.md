# Android 16 (API 36) Breaking Changes & Migration Guide

## Edge-to-Edge Mandatory

All apps targeting API 36 render edge-to-edge with no opt-out.

- `windowOptOutEdgeToEdgeEnforcement` is deprecated and disabled (no-op on API 36+)
- System bars (status bar, navigation bar) are transparent by default
- Content draws behind system bars unless insets are handled

### Migration

```kotlin
// Handle insets explicitly
ViewCompat.setOnApplyWindowInsetsListener(view) { v, insets ->
    val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
    v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
    insets
}

// Compose: use WindowInsets
Scaffold(
    contentWindowInsets = WindowInsets.systemBars
) { paddingValues -> ... }
```

### Checks

- `rg "windowOptOutEdgeToEdgeEnforcement"` -- remove all usages
- `rg "fitsSystemWindows"` -- verify not masking edge-to-edge issues
- Test with 3-button nav AND gesture nav (insets differ)

---

## Predictive Back Gesture Default

`onBackPressed()` is no longer called on API 36. The system uses `OnBackInvokedCallback` exclusively.

- `Activity.onBackPressed()` and `KeyEvent.KEYCODE_BACK` dispatching removed
- `KEYCODE_BACK` still dispatched for `onKeyDown()`/`onKeyUp()` but NOT for back navigation

### Migration

```kotlin
// Activity
onBackInvokedDispatcher.registerOnBackInvokedCallback(
    OnBackInvokedDispatcher.PRIORITY_DEFAULT
) {
    // handle back
}

// Fragment / Compose
val callback = object : OnBackPressedCallback(true) {
    override fun handleOnBackPressed() { /* ... */ }
}
onBackPressedDispatcher.addCallback(this, callback)
```

### Checks

- `rg "onBackPressed"` -- must replace every override
- `rg "KEYCODE_BACK"` -- verify not used for navigation logic
- Enable predictive back in developer options to test animations

---

## Adaptive Layouts on Large Screens (sw600dp+)

On devices with `sw >= 600dp`, the following manifest attributes are **IGNORED**:

- `android:screenOrientation`
- `android:resizableActivity`
- `android:minAspectRatio`
- `android:maxAspectRatio`

### Exemptions

- Games (`android.hardware.gamepad` or `android:appCategory="game"`) are exempt

### Migration

- Support all orientations and window sizes
- Use `WindowSizeClass` for adaptive layouts
- Test in multi-window, freeform, and folded/unfolded states
- Remove hardcoded orientation locks

### Checks

- `rg "screenOrientation" --glob "AndroidManifest.xml"` -- verify graceful handling
- `rg "resizableActivity" --glob "*.xml"` -- remove false values
- Test on tablets and foldables in all configurations

---

## JobScheduler Quota Enforcement

Runtime quotas are now enforced based on app standby bucket:

| Bucket | Quota Behavior |
|--------|---------------|
| Active | No quota limits |
| Working Set | Limited quota |
| Frequent | Reduced quota |
| Rare | Significantly reduced |
| Restricted | Minimal quota |

- Jobs exceeding quota are deferred until quota replenishes
- `JobScheduler.canRunJob()` added to check quota availability
- Expedited jobs have separate, smaller quota

### Migration

- Prefer WorkManager for deferrable work
- Use expedited jobs sparingly
- Monitor with `adb shell dumpsys jobscheduler`

---

## 16 KB Page Size Compatibility Mode

Android 16 runs on devices with 16 KB memory page sizes.

- Native code (NDK) must be compiled with 16 KB page alignment
- Apps not aligned run in compatibility mode with performance penalty
- Shared libraries must use `max-page-size=16384`

### Migration

```groovy
// build.gradle.kts
android {
    packaging {
        jniLibs {
            // Ensure 16KB alignment
            keepDebugSymbols += "**/*.so"
        }
    }
}
```

- Rebuild all native `.so` files with `-Wl,-z,max-page-size=16384`
- Verify with: `objdump -p lib.so | grep LOAD` (alignment should be 0x4000)

---

## Granular Health Permissions

`BODY_SENSORS` permission is split into granular permissions:

| Old Permission | New Permissions |
|---------------|----------------|
| `BODY_SENSORS` | `READ_HEART_RATE`, `READ_SKIN_TEMPERATURE`, `READ_BLOOD_OXYGEN`, etc. |

- Existing `BODY_SENSORS` grants auto-map to new permissions during upgrade
- New installs must request granular permissions

---

## Intent Redirection Protection

Default hardened against intent redirection attacks.

- System validates intents passed through `getParcelableExtra()` for redirect safety
- `intentMatchingFlags` attribute controls matching strictness
- Intents targeting unexported components from redirected extras are blocked

### Checks

- `rg "getParcelableExtra"` -- verify all intent extras are validated
- `rg "intent\.setComponent\|intent\.setClass"` -- check for redirect patterns

---

## Other Behavioral Changes

### elegantTextHeight Ignored

`elegantTextHeight` attribute on `TextView` is ignored. Text always renders with elegant (larger) height for complex scripts. Layouts may shift if they depended on `elegantTextHeight=false`.

### scheduleAtFixedRate

`ScheduledThreadPoolExecutor.scheduleAtFixedRate()` now runs only **one** missed execution when catching up, not all accumulated missed executions.

### MediaStore.getVersion()

`MediaStore.getVersion()` returns a per-app unique value. Cannot be used to detect media changes across apps.

### View.announceForAccessibility Deprecated

Use `AccessibilityManager.announce()` instead:

```kotlin
val am = getSystemService(AccessibilityManager::class.java)
am.announce(text, AccessibilityManager.FLAG_ANNOUNCE_POLITELY)
```

### Broadcast Priority

`android:priority` on broadcast receivers no longer affects cross-app ordering. Priority only applies within the same app.

---

## New APIs

### Notification.ProgressStyle

Rich progress notifications with segments, points, and tracker:

```kotlin
val style = Notification.ProgressStyle()
    .addProgressSegment(Notification.ProgressStyle.Segment(50))
    .addProgressPoint(Notification.ProgressStyle.Point(75))
notification.setStyle(style)
```

### RuntimeColorFilter & RuntimeXfermode

GPU-accelerated custom color filters and transfer modes using AGSL shaders.

### KeyStoreManager

New API for managing KeyStore entries with improved certificate chain handling.

### RangingManager

Ultra-Wideband (UWB) and Wi-Fi ranging with unified API surface.

### SystemHealthManager Headroom APIs

Query thermal and performance headroom to adapt workloads proactively:

```kotlin
val shm = getSystemService(SystemHealthManager::class.java)
val gpuHeadroom = shm.getGpuHeadroom()
val cpuHeadroom = shm.getCpuHeadroom()
```

### Embedded PhotoPicker

In-app photo picker without launching separate activity:

```kotlin
// Embed picker in your UI
val pickerFragment = PhotoPickerFragment()
supportFragmentManager.beginTransaction()
    .add(R.id.container, pickerFragment)
    .commit()
```
