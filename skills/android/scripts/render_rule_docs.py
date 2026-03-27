#!/usr/bin/env python3
"""Render markdown docs from the canonical rule registry."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "rules" / "rules.json"
REFERENCES_DIR = ROOT / "references"


def load_rules() -> dict:
    return json.loads(RULES_PATH.read_text())


def render_quality_gates(rules: dict) -> str:
    lines = [
        "# Quality Gates -- Generated from rules/rules.json",
        "",
        "This file is generated from the canonical registry at `skills/android/rules/rules.json`.",
        "",
        "## Critical Severity",
        "",
        "| ID | Category | Rule | External Evidence Required | Cap Behavior |",
        "|---|---|---|---|---|",
    ]
    for gate in rules["gates"]:
        if gate["severity"] != "critical":
            continue
        lines.append(
            f"| {gate['id']} | {gate['category']} | {gate['title']} | {'Yes' if gate['requires_external_evidence'] else 'No'} | {gate['cap_behavior']} |"
        )

    lines.extend(
        [
            "",
            "## High Severity",
            "",
            "| ID | Category | Rule | External Evidence Required | Cap Behavior |",
            "|---|---|---|---|---|",
        ]
    )
    for gate in rules["gates"]:
        if gate["severity"] != "high":
            continue
        lines.append(
            f"| {gate['id']} | {gate['category']} | {gate['title']} | {'Yes' if gate['requires_external_evidence'] else 'No'} | {gate['cap_behavior']} |"
        )

    lines.extend(
        [
            "",
            "## Score Caps",
            "",
            "| ID | When | Max Score |",
            "|---|---|---|",
        ]
    )
    for cap in rules["score_policy"]["caps"]:
        lines.append(f"| {cap['id']} | {cap['when']} | {cap['max_score']} |")

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Final scores require category scores plus gate evaluation.",
            "- External-evidence gates stay unresolved until telemetry or store artifacts are provided.",
            "- Preflight categories should report lower confidence when runtime or visual artifacts are missing.",
            "",
        ]
    )
    return "\n".join(lines)


def render_scoring_weights(rules: dict) -> str:
    lines = [
        "# Scoring Weights -- Generated from rules/rules.json",
        "",
        "This file is generated from the canonical registry at `skills/android/rules/rules.json`.",
        "",
        "## Category Weights",
        "",
        "| Category | Weight | Mode |",
        "|---|---|---|",
    ]
    for category in rules["category_weights"]:
        lines.append(
            f"| {category['label']} | {category['weight']}% | {category['audit_mode']} |"
        )

    lines.extend(
        [
            "",
            "## Score Policy",
            "",
            f"- Overall formula: `{rules['score_policy']['overall_formula']}`",
            f"- Requires category scores: `{rules['score_policy']['requires_category_scores']}`",
            f"- Insufficient evidence behavior: {rules['score_policy']['insufficient_evidence_behavior']}",
            "",
            "## Gate Summary",
            "",
            "| Severity | Count |",
            "|---|---|",
        ]
    )
    critical_count = sum(1 for gate in rules["gates"] if gate["severity"] == "critical")
    high_count = sum(1 for gate in rules["gates"] if gate["severity"] == "high")
    lines.append(f"| critical | {critical_count} |")
    lines.append(f"| high | {high_count} |")
    lines.append("")
    return "\n".join(lines)


def main():
    rules = load_rules()
    (REFERENCES_DIR / "quality-gates.md").write_text(render_quality_gates(rules))
    (REFERENCES_DIR / "scoring-weights.md").write_text(render_scoring_weights(rules))


if __name__ == "__main__":
    main()
