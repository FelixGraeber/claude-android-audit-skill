# claude-android-audit

Comprehensive Android project assessment skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Audits your Android project across 9 categories and produces a 0-100 health score with prioritized action plans.

Think of it as a senior Android engineer reviewing your entire project in under 2 minutes.

## What It Checks

| Category | Weight | What's Analyzed |
|----------|--------|----------------|
| **Architecture** | 15% | Compose adoption, UDF (ViewModel+StateFlow), DI (Hilt/Koin), Navigation 2.8+, module structure, repository pattern |
| **Performance** | 15% | Baseline Profiles, R8 config, app startup, Compose recomposition (stability, keys, derivedStateOf), memory, APK size |
| **Security** | 15% | OWASP Mobile Top 10 (2024), network config, crypto (Keystore/StrongBox), component security, WebView, supply chain |
| **Android 16 Compat** | 10% | Edge-to-edge enforcement, predictive back, large screen adaptation, 16KB pages, health permissions |
| **Design** | 10% | Material Design 3, M3 Expressive, dynamic color, WindowSizeClass, typography, component selection |
| **Accessibility** | 10% | Touch targets (48dp), content descriptions, Compose semantics, contrast, focus, headings |
| **Testing** | 10% | Compose tests, screenshot tests, Robolectric, test balance, coverage tools, CI/CD |
| **Build System** | 10% | Version catalogs, convention plugins, KSP vs KAPT, build perf, dependency verification |
| **Play Store** | 5% | Target SDK timeline, FGS types, data safety, permissions, ASO basics |

## Installation

```bash
claude install-skill FelixGraeber/claude-android-audit
```

Or add manually by cloning this repo and symlinking:

```bash
git clone https://github.com/FelixGraeber/claude-android-audit.git ~/.agents/skills/claude-android-audit

# Symlink skills
for skill in skills/android*; do
  ln -sf "$(pwd)/$skill" ~/.claude/skills/$(basename "$skill")
done

# Symlink agents
for agent in agents/android-*.md; do
  ln -sf "$(pwd)/$agent" ~/.claude/agents/$(basename "$agent")
done

# Install Python deps
cd skills/android && uv venv && uv pip install -r requirements.txt
```

## Usage

### Full Audit (9 parallel agents)
```
/android audit ~/path/to/android-project
```

Generates two reports:
- **ANDROID-AUDIT-REPORT.md** -- per-category scores and findings
- **ANDROID-ACTION-PLAN.md** -- prioritized fix list (Critical/High/Medium/Low)

### Individual Categories
```
/android architecture [path]   # Compose, UDF, DI, Navigation, modules
/android performance [path]    # Baseline Profiles, R8, startup, recomposition
/android security [path]       # OWASP 2024, network, crypto, WebView, supply chain
/android compat [path]         # Android 16: edge-to-edge, predictive back, large screens
/android design [path]         # M3, M3 Expressive, dynamic color, WindowSizeClass
/android accessibility [path]  # Touch targets, descriptions, semantics, contrast
/android testing [path]        # Compose tests, screenshots, CI/CD, coverage
/android build [path]          # Version catalogs, KSP, convention plugins
/android playstore [path]      # Target SDK, FGS types, data safety, policies
```

### Strategic Planning
```
/android plan [app-type]
```

App types: `social`, `ecommerce`, `fintech`, `health-fitness`, `productivity`, `generic`

Generates a 4-phase improvement roadmap tailored to your app type.

## Example Output

```
Overall Health Score: 66/100

Architecture      81  ████████░░
Performance       68  ██████▊░░░
Security          62  ██████▏░░░
Android 16        88  ████████▊░
Design            75  ███████▌░░
Accessibility     58  █████▊░░░░
Testing           18  █▊░░░░░░░░
Build System      56  █████▌░░░░
Play Store        82  ████████▏░
```

## How It Works

1. **Scan** -- discovers project structure (modules, build files, manifests, source counts)
2. **Extract** -- parses `build.gradle.kts`, `libs.versions.toml`, `AndroidManifest.xml`
3. **Classify** -- determines app type (single/multi-module, Compose/XML/hybrid, library)
4. **Dispatch** -- spawns 9 specialist agents in parallel, each analyzing their domain
5. **Aggregate** -- computes weighted health score from agent results
6. **Report** -- generates detailed findings and prioritized action plan

## Quality Gates

These rules are enforced regardless of score:

| Rule | Severity |
|------|----------|
| Exported component without permission | Critical |
| Cleartext traffic without network security config | Critical |
| targetSdk below Play Store requirement | Critical |
| Hardcoded secrets in source | Critical |
| `minifyEnabled = false` in release | Critical |
| KAPT when KSP alternative exists | High |
| No Baseline Profile | High |
| Touch targets < 48dp | High |
| No edge-to-edge implementation | High |

## Knowledge Sources

Built from extensive research of:
- [Android 16 (API 36)](https://developer.android.com/about/versions/16) behavioral changes and new APIs
- [OWASP Mobile Top 10 (2024)](https://owasp.org/www-project-mobile-top-10/) -- first major update since 2016
- [Material Design 3](https://m3.material.io/) and M3 Expressive guidelines
- [Android Vitals](https://developer.android.com/topic/performance/vitals) thresholds (crash >=1.09%, ANR >=0.47%)
- [Google Play policies](https://play.google.com/console/about/programs/target-api-level/) (target SDK timeline, data safety, FGS types)
- [Jetpack Compose](https://developer.android.com/develop/ui/compose/performance) performance patterns
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview) and R8 optimization
- [Gradle best practices](https://developer.android.com/build/optimize-your-build) (version catalogs, convention plugins, KSP)

## Repo Structure

```
claude-android-audit/
  skills/
    android/                    # Main orchestrator skill
      SKILL.md
      requirements.txt
      scripts/                  # Python analysis scripts
        scan_project.py         # Project structure discovery
        analyze_gradle.py       # Build config extraction
        analyze_manifest.py     # AndroidManifest.xml parsing
        analyze_compose.py      # Compose pattern static analysis
        analyze_dependencies.py # Dependency health check
        check_r8_config.py      # R8/ProGuard rule analysis
      references/               # Domain knowledge (loaded on-demand)
        android-16-changes.md
        owasp-mobile-2024.md
        material-design-3.md
        compose-best-practices.md
        play-store-policies.md
        quality-gates.md
        scoring-weights.md
        vitals-thresholds.md
    android-architecture/       # Sub-skill: architecture assessment
    android-performance/        # Sub-skill: performance audit
    android-security/           # Sub-skill: security audit
    android-compat/             # Sub-skill: Android 16 compatibility
    android-design/             # Sub-skill: Material Design review
    android-accessibility/      # Sub-skill: accessibility audit
    android-testing/            # Sub-skill: testing assessment
    android-build/              # Sub-skill: build system review
    android-playstore/          # Sub-skill: Play Store readiness
    android-audit/              # Sub-skill: full audit orchestration
    android-plan/               # Sub-skill: strategic planning
      templates/                # App-type specific roadmaps
  agents/                       # Agent definitions for parallel dispatch
    android-architecture.md
    android-performance.md
    android-security.md
    android-compat.md
    android-design.md
    android-accessibility.md
    android-testing.md
    android-build.md
    android-playstore.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI or IDE extension
- Python 3.11+ with [uv](https://docs.astral.sh/uv/) (for analysis scripts)
- An Android project with Gradle build system

## License

MIT
