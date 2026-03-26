#!/usr/bin/env python3
"""Analyze R8/ProGuard configuration for Android projects."""

import argparse
import json
import re
import sys
from pathlib import Path


def find_rule_files(root: Path) -> list[str]:
    files = []
    for pattern in ("proguard-rules.pro", "consumer-rules.pro", "proguard.cfg", "proguard-project.txt"):
        for p in root.rglob(pattern):
            if ".gradle" not in p.parts and "build" not in p.parts:
                files.append(str(p.relative_to(root)))
    return sorted(files)


def parse_rules(root: Path, rule_files: list[str]) -> dict:
    total_rules = 0
    keep_rules = 0
    overly_broad_keeps = []
    has_dont_optimize = False
    has_dont_obfuscate = False

    broad_patterns = [
        r"-keep\s+class\s+\*\*\s*\{\s*\*;\s*\}",
        r"-keep\s+class\s+!com\.",
        r"-keep\s+class\s+\*\s*\{\s*\*;\s*\}",
    ]

    for rel_path in rule_files:
        full_path = root / rel_path
        if not full_path.exists():
            continue
        try:
            text = full_path.read_text(errors="ignore")
        except OSError:
            continue

        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-"):
                total_rules += 1
                if line.startswith("-keep"):
                    keep_rules += 1
                if line.strip() == "-dontoptimize":
                    has_dont_optimize = True
                if line.strip() == "-dontobfuscate":
                    has_dont_obfuscate = True

        for pattern in broad_patterns:
            for m in re.finditer(pattern, text):
                rule = m.group(0).strip()
                if rule not in overly_broad_keeps:
                    overly_broad_keeps.append(rule)

        broad_keep_all = re.findall(r"-keep\s+class\s+[\w.]+\.\*\*\s*\{\s*\*;\s*\}", text)
        for rule in broad_keep_all:
            rule = rule.strip()
            if rule not in overly_broad_keeps:
                overly_broad_keeps.append(rule)

    return {
        "total_rules": total_rules,
        "keep_rules": keep_rules,
        "overly_broad_keeps": overly_broad_keeps,
        "has_dont_optimize": has_dont_optimize,
        "has_dont_obfuscate": has_dont_obfuscate,
    }


def check_build_config(root: Path) -> dict:
    uses_optimize_txt = False
    minify_enabled = False
    shrink_resources = False
    r8_full_mode = False

    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts and str(build_file).count(".gradle") > 1:
                continue
            if "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue

            if "proguard-android-optimize.txt" in text:
                uses_optimize_txt = True
            m = re.search(r"minifyEnabled\s*=?\s*(true|false)", text, re.IGNORECASE)
            if m and m.group(1).lower() == "true":
                minify_enabled = True
            m = re.search(r"shrinkResources\s*=?\s*(true|false)", text, re.IGNORECASE)
            if m and m.group(1).lower() == "true":
                shrink_resources = True

    gradle_props = root / "gradle.properties"
    if gradle_props.exists():
        try:
            text = gradle_props.read_text(errors="ignore")
            if "android.enableR8.fullMode=true" in text:
                r8_full_mode = True
            if re.search(r"android\.enableR8\.fullMode\s*=\s*true", text):
                r8_full_mode = True
        except OSError:
            pass

    return {
        "uses_optimize_txt": uses_optimize_txt,
        "minify_enabled": minify_enabled,
        "shrink_resources": shrink_resources,
        "r8_full_mode": r8_full_mode,
    }


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
        "minify_enabled": build_config["minify_enabled"],
        "shrink_resources": build_config["shrink_resources"],
        "r8_full_mode": build_config["r8_full_mode"],
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
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
