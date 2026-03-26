#!/usr/bin/env python3
"""Static analysis of Jetpack Compose patterns: stability, recomposition, accessibility, testing."""

import argparse
import json
import re
import sys
from pathlib import Path


def find_kt_files(root: Path) -> list[Path]:
    files = []
    for p in root.rglob("*.kt"):
        if ".gradle" not in p.parts and "build" not in p.parts:
            files.append(p)
    return files


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text))


def analyze_file(text: str, stats: dict):
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

    lazy_items_blocks = re.findall(r"items\s*\([^)]*\)", text)
    for block in lazy_items_blocks:
        if "key" in block:
            stats["lazy_keys_used"] += 1
        else:
            stats["lazy_keys_missing"] += 1

    item_blocks = re.findall(r"(?:itemsIndexed|item)\s*\([^)]*\)", text)
    for block in item_blocks:
        if "key" in block:
            stats["lazy_keys_used"] += 1

    stats["semantics_blocks"] += count_pattern(text, r"Modifier\s*\.\s*semantics\s*[\({]")
    stats["merge_descendants"] += count_pattern(text, r"mergeDescendants\s*=\s*true")
    stats["heading_annotations"] += count_pattern(text, r"heading\s*\(\s*\)")

    icon_calls = re.finditer(r"\bIcon\s*\(([^)]*)\)", text, re.DOTALL)
    for m in icon_calls:
        body = m.group(1)
        if "contentDescription" in body and "null" not in body.split("contentDescription")[1].split(",")[0]:
            stats["content_descriptions_present"] += 1
        else:
            stats["content_descriptions_missing"] += 1

    image_calls = re.finditer(r"\bImage\s*\(([^)]*)\)", text, re.DOTALL)
    for m in image_calls:
        body = m.group(1)
        if "contentDescription" in body and "null" not in body.split("contentDescription")[1].split(",")[0]:
            stats["content_descriptions_present"] += 1
        else:
            stats["content_descriptions_missing"] += 1

    clickable_calls = re.finditer(r"Modifier[^;{]*\.clickable\s*[\({][^}]*\}", text, re.DOTALL)
    for m in clickable_calls:
        block = m.group(0)
        if not re.search(r"\.size\s*\(|\.defaultMinSize\s*\(|\.sizeIn\s*\(|\.heightIn\s*\(|\.widthIn\s*\(", block):
            stats["small_touch_targets"] += 1

    stats["test_tags"] += count_pattern(text, r"testTag\s*\(")


def analyze(root: Path, mode: str) -> dict:
    kt_files = find_kt_files(root)

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
        "merge_descendants": 0,
        "heading_annotations": 0,
        "small_touch_targets": 0,
        "test_tags": 0,
    }

    for f in kt_files:
        try:
            text = f.read_text(errors="ignore")
        except OSError:
            continue
        analyze_file(text, stats)

    result = {"composable_count": stats["composable_count"]}

    if mode in ("stability", "all"):
        result["stability"] = {
            "stable_annotations": stats["stable_annotations"],
            "immutable_annotations": stats["immutable_annotations"],
            "data_classes_with_collections": stats["data_classes_with_collections"],
        }

    if mode in ("stability", "all"):
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
            "semantics_blocks": stats["semantics_blocks"],
            "merge_descendants": stats["merge_descendants"],
            "heading_annotations": stats["heading_annotations"],
            "small_touch_targets": stats["small_touch_targets"],
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
