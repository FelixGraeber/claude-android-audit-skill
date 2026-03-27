# claude-android-audit

Android audit and preflight skill pack for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

This repo now treats trust as a first-class requirement:

- one canonical rules registry
- one shared `audit-context.json` contract
- deterministic gate and cap evaluation
- explicit preflight boundaries where static source analysis is not enough

It is no longer described as a fully deterministic “senior Android engineer in under 2 minutes.” The goal is a defensible evidence pipeline first, richer judgment second.

## What It Produces

1. `generated/audit-context.json`
2. `ANDROID-AUDIT-REPORT.md`
3. `ANDROID-ACTION-PLAN.md`

The audit context is the shared machine-readable input for every category review.

## Category Weights

The canonical source is `skills/android/rules/rules.json`.

| Category | Weight | Mode |
|----------|--------|------|
| Architecture | 15% | Audit |
| Performance | 15% | Audit with external evidence preferred |
| Security | 15% | Audit |
| Compatibility | 10% | Audit |
| Design System Implementation | 10% | Preflight until visual artifacts exist |
| Accessibility | 10% | Preflight until runtime artifacts exist |
| Testing | 10% | Audit |
| Build System | 10% | Audit |
| Play Preflight | 5% | Preflight until store artifacts exist |

## Installation

```bash
claude install-skill FelixGraeber/claude-android-audit
```

Or add manually:

```bash
git clone https://github.com/FelixGraeber/claude-android-audit.git ~/.agents/skills/claude-android-audit

for skill in skills/android*; do
  ln -sf "$(pwd)/$skill" ~/.claude/skills/$(basename "$skill")
done

for agent in agents/android-*.md; do
  ln -sf "$(pwd)/$agent" ~/.claude/agents/$(basename "$agent")
done

cd skills/android && uv venv && uv pip install -r requirements.txt
```

## Usage

### Full Audit

```bash
/android audit ~/path/to/android-project
```

### Individual Categories

```bash
/android architecture [path]
/android performance [path]
/android security [path]
/android compat [path]
/android design [path]
/android accessibility [path]
/android testing [path]
/android build [path]
/android playstore [path]
```

## Evidence Pipeline

1. `scan_project.py` discovers modules and production source sets.
2. `analyze_gradle.py` extracts module-aware Gradle evidence.
3. `analyze_manifest.py` extracts per-manifest evidence and limitations.
4. `analyze_compose.py` emits static Compose evidence and low-confidence accessibility warnings.
5. `analyze_dependencies.py` and `check_r8_config.py` add build and dependency hygiene evidence.
6. `build_audit_context.py` assembles the shared `audit-context.json`.
7. `score.py` applies canonical gates and caps. If category scores are missing, it withholds the final 0-100 score.

## Canonical Sources

| Purpose | File |
|---|---|
| Rules and weights | `skills/android/rules/rules.json` |
| Time-sensitive facts | `skills/android/rules/facts.json` |
| Audit context schema | `skills/android/schemas/audit_context.schema.json` |
| Finding schema | `skills/android/schemas/finding.schema.json` |
| Generated quality gates doc | `skills/android/references/quality-gates.md` |
| Generated scoring doc | `skills/android/references/scoring-weights.md` |

## Current Limits

- Manifest analysis is still source-manifest based. Merged manifest support is a planned next step.
- Gradle analysis is file-based, not model-based.
- Performance, accessibility, design, and Play policy output remain preflight-quality until runtime or store artifacts are ingested.
- The repo still needs fixture projects and golden regression tests before claiming calibration.

## Repo Structure

```text
claude-android-audit/
  skills/android/
    SKILL.md
    rules/
      rules.json
      facts.json
    schemas/
      audit_context.schema.json
      finding.schema.json
    scripts/
      common.py
      scan_project.py
      analyze_gradle.py
      analyze_manifest.py
      analyze_compose.py
      analyze_dependencies.py
      check_r8_config.py
      build_audit_context.py
      render_rule_docs.py
      score.py
```

## License

MIT
