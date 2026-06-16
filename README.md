# claude-android-audit-skill

Claude Android Audit — Android Project Audit Skill Pack

Comprehensive Android audit and preflight skill pack for Claude Code. Reviews Android repos across architecture, performance, security, compatibility, design-system implementation, accessibility, testing, build health, and Play readiness, producing an audit report and prioritized action plan.

Built for evidence-based Android reviews: one shared audit context, category-specific analysis, and explicit trust boundaries where static source analysis is not enough.

## Features

- **Full repo audit**: run `/android audit <path>` to review an Android project end to end
- **Targeted checks**: architecture, performance, security, compatibility, design, accessibility, testing, build, and Play preflight
- **Shared evidence model**: every category review uses the same generated `audit-context.json`
- **Project-aware**: supports Kotlin, Java, Compose, XML/View apps, multi-module repos, and library-only projects
- **Confidence-aware output**: separates verified static findings, preflight warnings, and areas that need external evidence
- **Actionable deliverables**: generates `ANDROID-AUDIT-REPORT.md` and `ANDROID-ACTION-PLAN.md`

## Quick Start

Install with Claude Code:

```bash
claude install-skill FelixGraeber/claude-android-audit-skill
```

Or install manually:

```bash
git clone https://github.com/FelixGraeber/claude-android-audit-skill.git
cd claude-android-audit-skill

mkdir -p "${SKILLS_HOME:-$HOME/.claude/skills}" "${AGENTS_HOME:-$HOME/.claude/agents}"

for skill in skills/android*; do
  ln -sf "$(pwd)/$skill" "${SKILLS_HOME:-$HOME/.claude/skills}/$(basename "$skill")"
done

for agent in agents/android-*.md; do
  ln -sf "$(pwd)/$agent" "${AGENTS_HOME:-$HOME/.claude/agents}/$(basename "$agent")"
done

cd skills/android
uv venv
uv pip install -r requirements.txt
```

If your runtime uses different install locations, set `SKILLS_HOME` and `AGENTS_HOME` before running the commands above.

Then in Claude Code:

```bash
/android audit ~/path/to/android-project
/android security ~/path/to/android-project
/android performance ~/path/to/android-project
```

## Commands

| Command | Description |
|---------|-------------|
| `/android audit <path>` | Full multi-category Android audit |
| `/android architecture <path>` | Architecture, module structure, DI, navigation, and Compose adoption review |
| `/android performance <path>` | Static performance preflight for benchmarks, baseline profiles, shrink config, and Compose hints |
| `/android security <path>` | OWASP-oriented Android security review from static source and config evidence |
| `/android compat <path>` | Android 15/16 compatibility preflight, target SDK posture, predictive back, edge-to-edge |
| `/android design <path>` | Design-system implementation review from source evidence |
| `/android accessibility <path>` | Static accessibility preflight for semantics, labels, and touch-target risks |
| `/android testing <path>` | Testing strategy, coverage signals, screenshot tests, and CI maturity review |
| `/android build <path>` | Gradle, dependency, and release-build hygiene review |
| `/android playstore <path>` | Source-based Google Play preflight for permissions, manifests, and target SDK posture |
| `/android plan <app-type>` | 4-phase Android improvement roadmap |

## What It Produces

The full audit is designed to generate:

1. `generated/audit-context.json`
2. `ANDROID-AUDIT-REPORT.md`
3. `ANDROID-ACTION-PLAN.md`

The audit context is the shared machine-readable input for every category review.

## Project Detection

The audit confirms an Android project by scanning for common Android build and manifest files:

| Signal | Examples |
|--------|----------|
| Gradle build files | `build.gradle`, `build.gradle.kts` |
| Gradle settings | `settings.gradle`, `settings.gradle.kts` |
| Android manifests | `src/main/AndroidManifest.xml` |

It classifies repos before review so the output can reflect the actual project shape:

- application vs library-only repo
- single-module vs multi-module
- Compose-first vs XML-first vs hybrid

## Audit Pipeline

The full audit builds one shared evidence bundle, then uses that evidence across all category reviews:

1. `scan_project.py` discovers modules and production source sets
2. `analyze_gradle.py` extracts module-aware Gradle evidence
3. `analyze_manifest.py` extracts manifest evidence
4. `analyze_compose.py` extracts Compose and accessibility signals
5. `analyze_dependencies.py` and `check_r8_config.py` add dependency and shrinker evidence
6. `build_audit_context.py` assembles `generated/audit-context.json`
7. `score.py` applies canonical gates and score caps

## Evidence Model

The output is designed to be explicit about confidence:

- **Verified static findings**: strongly supported by source or config evidence
- **Preflight warnings**: likely risks inferred from static evidence
- **External evidence required**: areas that need screenshots, runtime traces, benchmarks, Play Console data, or other artifacts

If category evidence is incomplete, the scoring step can withhold a final 0-100 score instead of pretending confidence it does not have.

## Current Limits

- Manifest analysis is source-manifest based, not merged-manifest based
- Gradle analysis is file-based rather than model-based
- Performance claims need runtime metrics, benchmarks, traces, or Vitals data for high confidence
- Accessibility conclusions need runtime semantics, screenshots, and assistive-tech testing for high confidence
- Design review is stronger with screenshots, previews, or design specs
- Play review is a source-based preflight, not a substitute for Play Console configuration and policy review

## Repo Structure

```text
skills/android/            Main skill, rules, schemas, scripts, references
skills/android-*/          Category-specific skills
agents/android-*.md        Specialist audit agents
tests/                     Audit pipeline tests
```

## Requirements

- Python 3.12+
- Claude Code or another skill-compatible agent runtime
- `uv` recommended for dependency installation

## Local Checks

Run the focused Python test suite before changing audit scripts:

```bash
python3 -m unittest tests/test_audit_pipeline.py
python3 -m compileall -q skills/android/scripts tests
```

## License

MIT
