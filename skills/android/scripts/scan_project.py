#!/usr/bin/env python3
"""Discover Android project structure."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    count_compose_files,
    count_production_source_files,
    count_xml_layouts,
    discover_modules,
    production_source_files,
    relpath,
)


def find_named_files(root: Path, name: str) -> list[str]:
    files = []
    for path in root.rglob(name):
        if "build" in path.parts or ".gradle" in path.parts:
            continue
        files.append(relpath(root, path))
    return sorted(files)


def scan(root: Path) -> dict:
    modules = discover_modules(root)
    build_files = sorted(
        {
            module["build_file"]
            for module in modules
            if module.get("build_file")
        }
    )
    manifests = find_named_files(root, "AndroidManifest.xml")

    kt_files = production_source_files(root, (".kt",))
    java_files = production_source_files(root, (".java",))

    app_modules = [module["name"] for module in modules if module["kind"] == "application"]
    library_modules = [module["name"] for module in modules if module["kind"] == "library"]
    benchmark_modules = [
        module["name"]
        for module in modules
        if "benchmark" in module["name"].lower() or "macrobenchmark" in module["name"].lower()
    ]

    return {
        "modules": [module["name"] for module in modules],
        "module_details": modules,
        "build_files": build_files,
        "manifests": manifests,
        "source_counts": {
            "kt": len(kt_files),
            "java": len(java_files),
            "xml_layouts": count_xml_layouts(root),
            "compose_files": count_compose_files(root),
        },
        "module_counts": {
            "application": len(app_modules),
            "library": len(library_modules),
            "benchmark": len(benchmark_modules),
            "total": len(modules),
        },
        "application_modules": app_modules,
        "library_modules": library_modules,
        "has_version_catalog": (root / "gradle" / "libs.versions.toml").exists(),
        "has_convention_plugins": (root / "build-logic").exists(),
        "has_buildSrc": (root / "buildSrc").exists(),
        "has_benchmark_module": bool(benchmark_modules),
        "limitations": [
            "Structure scan uses source-set and build file heuristics.",
            "Merged manifest, Gradle model, and runtime artifacts are not available in this phase.",
        ],
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
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
