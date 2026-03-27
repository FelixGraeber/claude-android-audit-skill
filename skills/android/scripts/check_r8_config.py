#!/usr/bin/env python3
"""Analyze R8/ProGuard configuration for Android projects."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import discover_modules, read_text, relpath  # noqa: E402


def find_rule_files(root: Path) -> list[str]:
    files = []
    for pattern in ("proguard-rules.pro", "consumer-rules.pro", "proguard.cfg", "proguard-project.txt"):
        for path in root.rglob(pattern):
            if "build" in path.parts or ".gradle" in path.parts:
                continue
            files.append(relpath(root, path))
    return sorted(files)


def parse_rules(root: Path, rule_files: list[str]) -> dict:
    total_rules = 0
    keep_rules = 0
    overly_broad_keeps = []
    has_dont_optimize = False
    has_dont_obfuscate = False

    broad_patterns = [
        r"-keep\s+class\s+\*\*\s*\{\s*\*;\s*\}",
        r"-keep\s+class\s+\*\s*\{\s*\*;\s*\}",
        r"-keep\s+class\s+[\w.]+\.\*\*\s*\{\s*\*;\s*\}",
    ]

    for rel_path in rule_files:
        text = read_text(root / rel_path)
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("-"):
                total_rules += 1
                if stripped.startswith("-keep"):
                    keep_rules += 1
                if stripped == "-dontoptimize":
                    has_dont_optimize = True
                if stripped == "-dontobfuscate":
                    has_dont_obfuscate = True

        for pattern in broad_patterns:
            for match in re.finditer(pattern, text):
                rule = match.group(0).strip()
                if rule not in overly_broad_keeps:
                    overly_broad_keeps.append(rule)

    return {
        "total_rules": total_rules,
        "keep_rules": keep_rules,
        "overly_broad_keeps": overly_broad_keeps,
        "has_dont_optimize": has_dont_optimize,
        "has_dont_obfuscate": has_dont_obfuscate,
    }


def extract_release_block(text: str) -> str:
    match = re.search(r"buildTypes\s*\{.*?release\s*\{(.*?)\n\s*}", text, re.DOTALL)
    return match.group(1) if match else ""


def check_build_config(root: Path) -> dict:
    module_release_settings = []
    uses_optimize_txt = False

    for module in discover_modules(root):
        build_file_rel = module.get("build_file")
        if not build_file_rel:
            continue
        build_file = root / build_file_rel
        text = read_text(build_file)
        release_block = extract_release_block(text)
        if "proguard-android-optimize.txt" in text:
            uses_optimize_txt = True

        module_release_settings.append(
            {
                "module": module["name"],
                "kind": module["kind"],
                "build_file": build_file_rel,
                "release_minify_enabled": match_bool(release_block, r"minifyEnabled\s*=?\s*(true|false)"),
                "release_shrink_resources": match_bool(release_block, r"shrinkResources\s*=?\s*(true|false)"),
            }
        )

    gradle_properties_text = read_text(root / "gradle.properties")
    bad_gradle_properties = []
    for key in ("android.enableR8.fullMode", "android.nonTransitiveRClass"):
        match = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", gradle_properties_text, re.MULTILINE)
        if match and match.group(1).strip().lower() == "false":
            bad_gradle_properties.append(f"{key}=false")

    app_release_configs = [entry for entry in module_release_settings if entry["kind"] == "application"]
    protected_release_modules = [
        entry["module"]
        for entry in app_release_configs
        if entry["release_minify_enabled"] is True
    ]

    return {
        "uses_optimize_txt": uses_optimize_txt,
        "module_release_settings": module_release_settings,
        "protected_release_modules": protected_release_modules,
        "all_application_release_variants_protected": bool(app_release_configs) and len(protected_release_modules) == len(app_release_configs),
        "bad_gradle_properties": bad_gradle_properties,
    }


def match_bool(text: str, pattern: str) -> bool | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).lower() == "true"


def analyze(root: Path) -> dict:
    rule_files = find_rule_files(root)
    rules = parse_rules(root, rule_files)
    build_config = check_build_config(root)

    return {
        "rule_files": rule_files,
        "total_rules": rules["total_rules"],
        "keep_rules": rules["keep_rules"],
        "overly_broad_keeps": rules["overly_broad_keeps"],
        "has_dont_optimize": rules["has_dont_optimize"],
        "has_dont_obfuscate": rules["has_dont_obfuscate"],
        "uses_optimize_txt": build_config["uses_optimize_txt"],
        "module_release_settings": build_config["module_release_settings"],
        "protected_release_modules": build_config["protected_release_modules"],
        "all_application_release_variants_protected": build_config["all_application_release_variants_protected"],
        "bad_gradle_properties": build_config["bad_gradle_properties"],
        "limitations": [
            "Release build detection is static and may miss convention-plugin indirection.",
            "R8 effectiveness still requires build output or mapping artifacts.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze R8/ProGuard configuration")
    parser.add_argument("path", help="Path to project root")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}), file=sys.stderr)
        sys.exit(1)

    result = analyze(root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
