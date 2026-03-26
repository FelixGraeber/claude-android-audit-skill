# Scoring Weights

## Category Weights

| Category | Weight | Justification |
|----------|--------|---------------|
| Architecture & Patterns | 15% | Foundation for maintainability and scalability. Poor architecture compounds into every other category over time. |
| Performance | 15% | Direct user experience impact. Startup time, frame drops, and memory usage affect retention. Play Store ranking factor via Android Vitals. |
| Security | 15% | User trust, regulatory compliance, data protection. A single breach can destroy an app's reputation. Non-negotiable for fintech/health. |
| Android 16 Compatibility | 10% | Forward compatibility with latest platform. Play Store target SDK deadlines make this a hard requirement on a timeline. |
| UI/UX & Design | 10% | User experience, brand perception, conversion rates. Material Design compliance signals quality to users. |
| Accessibility | 10% | Inclusivity, legal compliance (ADA/EAA), expanded audience (~15% of population has a disability). |
| Testing | 10% | Quality assurance, regression prevention, refactoring confidence. Enables safe iteration velocity. |
| Build & Dependencies | 10% | Developer productivity, build times, supply chain security. Slow builds compound into lost engineering hours. |
| Play Store Readiness | 5% | Distribution readiness. Lower weight because it's partially covered by Security, Compatibility, and Performance categories. |

**Total: 100%**

---

## Sub-Category Scoring by Agent

### Architecture & Patterns Agent (15%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Compose Adoption | 25% | % of screens in Compose, interop quality if mixed |
| UDF / State Management | 25% | ViewModel + StateFlow, MVI pattern, no logic in UI |
| Dependency Injection | 20% | Hilt/Koin setup, proper scoping, no manual DI |
| Navigation | 15% | Type-safe routes, single NavHost, deep link handling |
| Module Structure | 15% | Feature modules, dependency direction, API/impl split |

### Performance Agent (15%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| App Startup | 25% | Cold start time, Baseline Profile, App Startup library |
| Compose Recomposition | 25% | Stability annotations, derivedStateOf, deferred reads |
| Memory Management | 20% | LeakCanary integration, bitmap handling, cache policies |
| ANR Prevention | 15% | Main thread discipline, StrictMode, coroutine usage |
| APK/AAB Size | 15% | R8 shrinking, resource optimization, split APKs |

### Security Agent (15%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Network Security | 20% | TLS config, cert pinning, network_security_config.xml |
| Data Storage | 20% | Encryption at rest, Keystore usage, no plaintext secrets |
| Component Security | 20% | Exported components, intent validation, permissions |
| Cryptography | 15% | Algorithm strength, key management, RNG quality |
| WebView Hardening | 10% | JS disabled/controlled, file access, SSL error handling |
| Supply Chain | 15% | Dependency verification, trusted repos, update cadence |

### Android 16 Compatibility Agent (10%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Edge-to-Edge | 30% | Inset handling, no opt-out usage, system bar behavior |
| Predictive Back | 25% | OnBackInvokedCallback, no onBackPressed overrides |
| Large Screen Adaptation | 20% | WindowSizeClass, adaptive layouts, orientation handling |
| API Changes | 15% | elegantTextHeight, scheduleAtFixedRate, MediaStore changes |
| 16KB Page Alignment | 10% | Native library alignment (only if NDK used) |

### UI/UX & Design Agent (10%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Material Design 3 | 30% | Correct component usage, color roles, typography |
| Dynamic Color | 20% | dynamicColorScheme implementation, fallback themes |
| Responsive Layout | 25% | WindowSizeClass, canonical layouts, navigation adaptation |
| Typography & Color | 15% | sp units, contrast ratios, role consistency |
| M3 Expressive | 10% | Appropriate intensity, hero moments, shape/motion |

### Accessibility Agent (10%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Touch Targets | 25% | Minimum 48dp, spacing between targets |
| Content Descriptions | 25% | All interactive elements labeled, decorative marked |
| TalkBack Support | 20% | Focus order, traversal, announcements |
| Compose Semantics | 15% | Proper semantic tree, heading levels, roles |
| Color & Contrast | 15% | WCAG AA compliance, non-color indicators |

### Testing Agent (10%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Unit Tests | 25% | ViewModel/UseCase coverage, assertion quality |
| Compose UI Tests | 25% | ComposeTestRule, semantic matchers, interaction tests |
| Screenshot Tests | 20% | Roborazzi/Paparazzi setup, design system coverage |
| Integration Tests | 15% | Repository/database tests, API contract tests |
| CI/CD | 15% | Automated test execution, coverage gates, lint checks |

### Build & Dependencies Agent (10%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Version Catalog | 25% | libs.versions.toml, consistent versioning |
| Convention Plugins | 20% | Shared build logic, no copy-paste config |
| KSP vs KAPT | 20% | KSP adopted where available, no unnecessary KAPT |
| Build Performance | 20% | Configuration cache, build cache, parallel execution |
| Dependency Hygiene | 15% | No unused deps, verification metadata, no SNAPSHOTs |

### Play Store Readiness Agent (5%)

| Sub-Category | Weight Within Category | What Is Scored |
|-------------|----------------------|----------------|
| Target SDK | 30% | Meets current requirement (35+) |
| Data Safety | 25% | Permissions declared match actual usage |
| Foreground Services | 20% | Types declared, permissions present |
| Policy Compliance | 15% | Ad rules, subscription rules, account deletion |
| Store Listing | 10% | ASO basics, screenshots, description quality |

---

## Score Calculation

```
final_score = sum(category_weight * category_score for each category)
```

Where `category_score` is 0-100, calculated from its sub-categories.

### Score Caps (Quality Gates)

- Any Critical quality gate violation: **final score capped at 40**
- 3+ High quality gate violations: **final score capped at 60**
- Critical violation in Security: **Security category score = 0**

### Score Interpretation

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | Excellent | Production-ready, minimal improvements needed |
| 75-89 | Good | Solid foundation, address high-priority items |
| 60-74 | Fair | Significant gaps, prioritize fixes before release |
| 40-59 | Poor | Major issues, substantial work needed |
| 0-39 | Critical | Fundamental problems, likely has critical gate violations |
