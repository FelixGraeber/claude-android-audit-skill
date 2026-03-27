#!/usr/bin/env python3
"""Apply deterministic gate and cap logic to an audit context."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def get(data: dict, path: str):
    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def evaluate_gate(gate: dict, context: dict) -> tuple[str, bool | None]:
    if gate["id"] == "C1":
        return ("manifest.exported_components", any(not component.get("has_permission") for component in context["manifest"].get("exported_components", [])))
    if gate["id"] == "C2":
        return ("manifest.cleartext_without_nsc", context["manifest"].get("uses_cleartext") is True and context["manifest"].get("has_network_security_config") is False)
    if gate["id"] == "C3":
        target_sdk = context["gradle"].get("target_sdk")
        return ("gradle.target_sdk", target_sdk is not None and target_sdk < 35)
    if gate["id"] == "C4":
        return ("security.hardcoded_secrets_count", context["security"].get("hardcoded_secrets_count", 0) > 0)
    if gate["id"] == "C5":
        return ("external.vitals.crash_rate", None)
    if gate["id"] == "C6":
        return ("external.vitals.anr_rate", None)
    if gate["id"] == "C7":
        return ("r8.all_application_release_variants_protected", context["r8"].get("all_application_release_variants_protected") is False)
    if gate["id"] == "C8":
        return ("manifest.debuggable", context["manifest"].get("debuggable") is True)
    if gate["id"] == "H1":
        return ("gradle.uses_kapt", context["gradle"].get("uses_kapt") is True)
    if gate["id"] == "H2":
        return ("scan.has_benchmark_module", context["scan"].get("has_benchmark_module") is False)
    if gate["id"] == "H3":
        value = get(context, "compose.accessibility.small_touch_target_warnings")
        return ("compose.accessibility.small_touch_target_warnings", bool(value))
    if gate["id"] == "H4":
        return ("dependencies.deprecated_deps", any(dep.get("name") == "security-crypto" for dep in context["dependencies"].get("deprecated_deps", [])))
    if gate["id"] == "H5":
        return ("compat.edge_to_edge_signal", context["compat"].get("edge_to_edge_signal") is False)
    if gate["id"] == "H6":
        return ("manifest.has_network_security_config", context["manifest"].get("has_network_security_config") is False)
    if gate["id"] == "H7":
        return ("security.webview_ssl_proceed_count", context["security"].get("webview_ssl_proceed_count", 0) > 0)
    if gate["id"] == "H8":
        return ("compat.uses_on_back_pressed", context["compat"].get("uses_on_back_pressed") is True)
    return ("unknown", None)


def evaluate(context: dict, rules: dict, category_scores: dict | None) -> dict:
    triggered = []
    unresolved = []
    for gate in rules["gates"]:
        evidence_key, result = evaluate_gate(gate, context)
        payload = {
            "id": gate["id"],
            "severity": gate["severity"],
            "title": gate["title"],
            "category": gate["category"],
            "evidence_key": evidence_key,
            "requires_external_evidence": gate["requires_external_evidence"],
        }
        if result is None:
            unresolved.append(payload)
        elif result:
            triggered.append(payload)

    critical_count = sum(1 for gate in triggered if gate["severity"] == "critical")
    high_count = sum(1 for gate in triggered if gate["severity"] == "high")

    caps = []
    if critical_count:
        caps.append({"id": "critical-cap", "max_score": 40})
    if high_count >= 3:
        caps.append({"id": "high-cap", "max_score": 60})

    result = {
        "gates_triggered": triggered,
        "gates_unresolved": unresolved,
        "score_caps_applied": caps,
        "formula_trace": [],
        "confidence": 0.45 if unresolved else 0.65,
    }

    if not category_scores:
        result["status"] = "insufficient_evidence_for_final_score"
        result["message"] = "Category scores were not provided. Gate results are deterministic, but the final 0-100 score is withheld."
        return result

    total = 0.0
    for category in rules["category_weights"]:
        category_id = category["id"]
        if category_id not in category_scores:
            continue
        weighted = category_scores[category_id] * category["weight"] / 100
        total += weighted
        result["formula_trace"].append(
            {
                "category": category_id,
                "raw_score": category_scores[category_id],
                "weight": category["weight"],
                "weighted_score": weighted,
            }
        )

    final_score = total
    for cap in caps:
        final_score = min(final_score, cap["max_score"])

    result["status"] = "scored"
    result["final_score"] = round(final_score, 2)
    return result


def main():
    parser = argparse.ArgumentParser(description="Apply canonical score caps to an audit context")
    parser.add_argument("audit_context", help="Path to audit-context.json")
    parser.add_argument("--category-scores", help="Optional JSON file containing category scores keyed by category id")
    args = parser.parse_args()

    context = json.loads(Path(args.audit_context).read_text())
    rules_path = Path(context["rules"]["path"])
    rules = json.loads(rules_path.read_text())
    category_scores = json.loads(Path(args.category_scores).read_text()) if args.category_scores else None

    print(json.dumps(evaluate(context, rules, category_scores), indent=2))


if __name__ == "__main__":
    main()
