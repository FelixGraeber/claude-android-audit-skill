#!/usr/bin/env python3
"""Discover Android project structure."""

import argparse
import json
import re
import sys
from pathlib import Path


def find_files(root: Path, name: str) -> list[str]:
    return [str(p.relative_to(root)) for p in root.rglob(name) if ".gradle" not in p.parts and "build" not in p.parts]


def count_files(root: Path, suffix: str) -> int:
    return sum(1 for _ in root.rglob(f"*{suffix}") if ".gradle" not in _.parts and "build" not in _.parts)


def count_xml_layouts(root: Path) -> int:
    count = 0
    for p in root.rglob("*.xml"):
        parts = p.parts
        if any(part.startswith("layout") for part in parts) and "res" in parts:
            if ".gradle" not in parts and "build" not in parts:
                count += 1
    return count


def count_compose_files(root: Path) -> int:
    count = 0
    for p in root.rglob("*.kt"):
        if ".gradle" in p.parts or "build" in p.parts:
            continue
        try:
            text = p.read_text(errors="ignore")
            if "@Composable" in text:
                count += 1
        except OSError:
            continue
    return count


def parse_modules(root: Path) -> list[str]:
    modules = []
    for name in ("settings.gradle.kts", "settings.gradle"):
        settings = root / name
        if settings.exists():
            try:
                text = settings.read_text(errors="ignore")
                for m in re.findall(r'include\s*\(\s*"([^"]+)"\s*\)', text):
                    modules.append(m.lstrip(":").replace(":", "/"))
                for m in re.findall(r"include\s*\(\s*'([^']+)'\s*\)", text):
                    modules.append(m.lstrip(":").replace(":", "/"))
                for m in re.findall(r'include\s+"([^"]+)"', text):
                    modules.append(m.lstrip(":").replace(":", "/"))
                for m in re.findall(r"include\s+'([^']+)'", text):
                    modules.append(m.lstrip(":").replace(":", "/"))
            except OSError:
                continue
            break
    return sorted(set(modules))


def scan(root: Path) -> dict:
    build_files = find_files(root, "build.gradle.kts") + find_files(root, "build.gradle")
    manifests = find_files(root, "AndroidManifest.xml")
    modules = parse_modules(root)

    kt_count = count_files(root, ".kt")
    java_count = count_files(root, ".java")
    xml_layouts = count_xml_layouts(root)
    compose_files = count_compose_files(root)

    has_version_catalog = (root / "gradle" / "libs.versions.toml").exists()
    has_convention_plugins = (root / "build-logic").exists()
    has_buildsrc = (root / "buildSrc").exists()
    has_benchmark = any(
        "benchmark" in m.lower() or "macrobenchmark" in m.lower()
        for m in modules
    )

    return {
        "modules": modules,
        "build_files": sorted(build_files),
        "manifests": sorted(manifests),
        "source_counts": {
            "kt": kt_count,
            "java": java_count,
            "xml_layouts": xml_layouts,
            "compose_files": compose_files,
        },
        "has_version_catalog": has_version_catalog,
        "has_convention_plugins": has_convention_plugins,
        "has_buildSrc": has_buildsrc,
        "has_benchmark_module": has_benchmark,
    }


def main():
    parser = argparse.ArgumentParser(description="Scan Android project structure")
    parser.add_argument("path", help="Path to project root")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}), file=sys.stderr)
        sys.exit(1)

    result = scan(root)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
