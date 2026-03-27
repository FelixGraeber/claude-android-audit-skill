#!/usr/bin/env python3
"""Static analysis of Jetpack Compose patterns."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import production_source_files, relpath  # noqa: E402


CALL_BLOCK_RE = re.compile(r"\b(Icon|Image|AsyncImage)\s*\((.*?)\)", re.DOTALL)


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text))


def append_issue(issues: list[dict], root: Path, file_path: Path, rule_id: str, line: int, message: str, confidence: float):
    issues.append(
        {
            "rule_id": rule_id,
            "file": relpath(root, file_path),
            "line": line,
            "message": message,
            "confidence": confidence,
        }
    )


def analyze_file(root: Path, file_path: Path, text: str, stats: dict):
    stats["composable_count"] += count_pattern(text, r"@Composable")
    stats["stable_annotations"] += count_pattern(text, r"@Stable\b")
    stats["immutable_annotations"] += count_pattern(text, r"@Immutable\b")
    stats["data_classes_with_collections"] += count_pattern(
        text, r"data\s+class\s+\w+[^)]*\b(?:List|Map|Set|MutableList|MutableMap|MutableSet)\b"
    )
    stats["derived_state_of"] += count_pattern(text, r"derivedStateOf\s*\{")
    stats["remember_usage"] += count_pattern(text, r"\bremember(?:Saveable)?\s*[\({]")
    stats["collect_as_state_with_lifecycle"] += count_pattern(text, r"collectAsStateWithLifecycle\s*\(")
    stats["collect_as_state_without_lifecycle"] += count_pattern(text, r"collectAsState\s*\(")
    stats["semantics_blocks"] += count_pattern(text, r"Modifier\s*\.\s*(?:semantics|clearAndSetSemantics)\s*[\({]")
    stats["merge_descendants"] += count_pattern(text, r"mergeDescendants\s*=\s*true")
    stats["heading_annotations"] += count_pattern(text, r"heading\s*\(\s*\)")
    stats["pane_titles"] += count_pattern(text, r"paneTitle\s*=")
    stats["live_regions"] += count_pattern(text, r"liveRegion\s*=")
    stats["test_tags"] += count_pattern(text, r"testTag\s*\(")

    for block in re.findall(r"(?:items|itemsIndexed|item)\s*\((.*?)\)", text, re.DOTALL):
        if "key" in block:
            stats["lazy_keys_used"] += 1
        else:
            stats["lazy_keys_missing"] += 1

    for match in CALL_BLOCK_RE.finditer(text):
        component = match.group(1)
        body = match.group(2)
        line = line_number(text, match.start())
        if "contentDescription" not in body:
            stats["content_descriptions_missing"] += 1
            append_issue(
                stats["issues"],
                root,
                file_path,
                "compose.missing_content_description",
                line,
                f"{component} is missing an explicit contentDescription. Decorative assets should use contentDescription = null.",
                0.55,
            )
            continue

        description_arg = re.search(r"contentDescription\s*=\s*([^,\n]+)", body)
        if description_arg and description_arg.group(1).strip() == "null":
            stats["decorative_content_descriptions"] += 1
        else:
            stats["content_descriptions_present"] += 1

    for matcher, rule_id, message in (
        (r"\.clickable\s*\(", "compose.low_confidence_touch_target", "Clickable modifier without local size hint."),
        (r"\.toggleable\s*\(", "compose.low_confidence_touch_target", "Toggleable modifier without local size hint."),
        (r"\.selectable\s*\(", "compose.low_confidence_touch_target", "Selectable modifier without local size hint."),
    ):
        for match in re.finditer(matcher, text):
            line = line_number(text, match.start())
            window = text[max(0, match.start() - 180): min(len(text), match.end() + 180)]
            if re.search(
                r"minimumInteractiveComponentSize\s*\(|\.size(In)?\s*\(|\.defaultMinSize\s*\(|\.heightIn\s*\(|\.widthIn\s*\(",
                window,
            ):
                continue
            stats["small_touch_target_warnings"] += 1
            append_issue(
                stats["issues"],
                root,
                file_path,
                rule_id,
                line,
                message,
                0.3,
            )


def analyze(root: Path, mode: str) -> dict:
    files = production_source_files(root, (".kt",))
    stats = {
        "composable_count": 0,
        "stable_annotations": 0,
        "immutable_annotations": 0,
        "data_classes_with_collections": 0,
        "derived_state_of": 0,
        "lazy_keys_used": 0,
        "lazy_keys_missing": 0,
        "remember_usage": 0,
        "collect_as_state_with_lifecycle": 0,
        "collect_as_state_without_lifecycle": 0,
        "semantics_blocks": 0,
        "content_descriptions_present": 0,
        "content_descriptions_missing": 0,
        "decorative_content_descriptions": 0,
        "merge_descendants": 0,
        "heading_annotations": 0,
        "pane_titles": 0,
        "live_regions": 0,
        "small_touch_target_warnings": 0,
        "test_tags": 0,
        "issues": [],
    }

    for file_path in files:
        analyze_file(root, file_path, file_path.read_text(errors="ignore"), stats)

    result = {"composable_count": stats["composable_count"]}

    if mode in ("stability", "all"):
        result["stability"] = {
            "stable_annotations": stats["stable_annotations"],
            "immutable_annotations": stats["immutable_annotations"],
            "data_classes_with_collections": stats["data_classes_with_collections"],
        }
        result["recomposition"] = {
            "derived_state_of": stats["derived_state_of"],
            "lazy_keys_used": stats["lazy_keys_used"],
            "lazy_keys_missing": stats["lazy_keys_missing"],
            "remember_usage": stats["remember_usage"],
            "collect_as_state_with_lifecycle": stats["collect_as_state_with_lifecycle"],
            "collect_as_state_without_lifecycle": stats["collect_as_state_without_lifecycle"],
        }

    if mode in ("accessibility", "all"):
        result["accessibility"] = {
            "content_descriptions_present": stats["content_descriptions_present"],
            "content_descriptions_missing": stats["content_descriptions_missing"],
            "decorative_content_descriptions": stats["decorative_content_descriptions"],
            "semantics_blocks": stats["semantics_blocks"],
            "merge_descendants": stats["merge_descendants"],
            "heading_annotations": stats["heading_annotations"],
            "pane_titles": stats["pane_titles"],
            "live_regions": stats["live_regions"],
            "small_touch_target_warnings": stats["small_touch_target_warnings"],
            "issues": stats["issues"],
            "limitations": [
                "Touch target and semantics checks are static heuristics with low confidence.",
                "Contrast, focus order, and TalkBack behavior require screenshots or runtime semantics dumps.",
            ],
        }

    result["testing"] = {"test_tags": stats["test_tags"]}
    return result


def main():
    parser = argparse.ArgumentParser(description="Static analysis of Compose patterns")
    parser.add_argument("path", help="Path to project root")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--mode", choices=["stability", "accessibility", "all"], default="all", help="Analysis mode")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}), file=sys.stderr)
        sys.exit(1)

    result = analyze(root, args.mode)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
