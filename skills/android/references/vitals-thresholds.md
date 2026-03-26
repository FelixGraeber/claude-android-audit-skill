# Android Vitals -- Bad Behavior Thresholds

## Core Metrics

| Metric | Good | Warning | Bad Behavior | Source |
|--------|------|---------|-------------|--------|
| User-perceived crash rate | < 0.5% | 0.5% - 1.09% | >= 1.09% | Play Console > Android Vitals |
| User-perceived ANR rate | < 0.1% | 0.1% - 0.47% | >= 0.47% | Play Console > Android Vitals |
| Excessive wakeups | < 10/hr | 10 - 60/hr | >= 60/hr | AlarmManager misuse |
| Stuck partial wake locks | < 0.3% | 0.3% - 1% | >= 1% | Sessions with stuck locks |

All metrics measured as a percentage of daily active sessions over a **28-day rolling window**.

---

## Wake Lock Enforcement

| Rule | Detail |
|------|--------|
| Threshold | > 2 hours cumulative wake lock held per 24-hour period |
| Affected | Sessions where wake lock exceeds threshold as % of total sessions > 5% |
| March 2026 | Wake lock violators **excluded from Play Store recommendations** |
| Impact | Loss of "suggested for you", "similar apps", editorial features |

### Prevention

- Use `WorkManager` instead of manual wake locks for background work
- Always release wake locks in `finally` blocks or `onDestroy`
- Set wake lock timeout: `wakeLock.acquire(10 * 60 * 1000L)` (10 min max)
- Monitor with `adb shell dumpsys power | grep -i wake`

---

## App Startup Thresholds

| Start Type | Definition | Excessive Threshold |
|------------|-----------|-------------------|
| Cold start | App process not running, full initialization | >= 5 seconds |
| Warm start | Process exists, Activity needs recreation | >= 2 seconds |
| Hot start | Process and Activity exist, just brought to foreground | >= 1.5 seconds |

### Measurement

- Measured from `Zygote.fork()` to first frame fully drawn
- Includes `Application.onCreate()`, `Activity.onCreate()`, layout inflation, first draw
- `reportFullyDrawn()` for accurate TTFD (Time To Full Display)

### Optimization Targets

| Start Type | Target | Stretch Goal |
|------------|--------|-------------|
| Cold start | < 2 seconds | < 1 second |
| Warm start | < 1 second | < 500ms |
| Hot start | < 500ms | < 200ms |

---

## ANR Timeout Reference

| Scenario | Timeout |
|----------|---------|
| Input dispatching (foreground Activity) | 5 seconds |
| Service.onCreate / onStartCommand / onBind | ~10 seconds |
| Foreground service not calling startForeground() | 5 seconds |
| Broadcast receiver (foreground app) | 5 seconds |
| Broadcast receiver (background) | ~10 seconds |
| JobService.onStartJob / onStopJob | Several seconds |
| ContentProvider.onCreate | ~10 seconds |

---

## Data Window & Fix Policy

| Policy | Detail |
|--------|--------|
| Data window | 28-day rolling aggregate |
| Emerging issue detection | New issues flagged within 7 days |
| Fix window | 21 days from notification to resolve before penalties escalate |
| Device segmentation | Thresholds apply per device type (phone, tablet, watch, auto, TV) |
| Country segmentation | Vitals shown per country; bad behavior is global aggregate |
| Minimum sample | Thresholds only apply once minimum session count is reached |
| Opt-in only | Only users who share usage & diagnostics contribute data |

---

## Penalties for Bad Behavior

| Level | Trigger | Consequence |
|-------|---------|-------------|
| Warning | Any metric crosses bad behavior threshold | Warning badge visible to users in Play Store |
| Visibility reduction | Sustained bad behavior (28+ days) | Lower ranking in search and browse, fewer impressions |
| Recommendation exclusion | Persistent violation or wake lock violation (March 2026) | Excluded from "Suggested for you", editorial, and similar app recommendations |
| Extreme | Severe or worsening metrics | App may be removed from some surfaces entirely |

---

## Monitoring Checklist

- [ ] Play Console > Android Vitals dashboard reviewed weekly
- [ ] Crash reporting SDK integrated (Firebase Crashlytics, Sentry, Bugsnag)
- [ ] ANR detection: StrictMode in debug, background thread discipline
- [ ] Wake lock audit: `rg "newWakeLock\|acquire" --type kotlin`
- [ ] Alarm audit: `rg "AlarmManager\|setExact\|setRepeating" --type kotlin`
- [ ] Startup tracing: `adb shell am start -W` for cold start measurement
- [ ] Baseline Profile generated and updated per release
- [ ] `reportFullyDrawn()` called after meaningful content displayed
- [ ] CI pipeline includes startup benchmarks (Macrobenchmark library)

---

## Key API References

```kotlin
// Report fully drawn (accurate TTFD)
reportFullyDrawn()

// Macrobenchmark for CI
@LargeTest
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startup() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }
}

// Wake lock with timeout (never unlimited)
val wakeLock = powerManager.newWakeLock(
    PowerManager.PARTIAL_WAKE_LOCK, "app:mytag"
)
wakeLock.acquire(10 * 60 * 1000L) // 10 minute max
try {
    doWork()
} finally {
    if (wakeLock.isHeld) wakeLock.release()
}
```
