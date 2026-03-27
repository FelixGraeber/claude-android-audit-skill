#!/usr/bin/env python3
"""Parse Android build configuration from Gradle files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import (  # noqa: E402
    discover_modules,
    iter_gradle_build_files,
    parse_version_catalog,
    read_text,
    relpath,
)


def match_int(text: str, pattern: str) -> int | None:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def match_bool(text: str, pattern: str) -> bool | None:
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    return match.group(1).lower() == "true"


def extract_release_block(text: str) -> str:
    match = re.search(r"buildTypes\s*\{.*?release\s*\{(.*?)\n\s*}", text, re.DOTALL)
    return match.group(1) if match else ""


def extract_plugins(text: str) -> list[str]:
    plugins = set(re.findall(r'id\s*\(\s*["\']([^"\']+)["\']\s*\)', text))
    plugins.update(re.findall(r'kotlin\s*\(\s*["\']([^"\']+)["\']\s*\)', text))
    return sorted(plugins)


def module_details(root: Path) -> list[dict]:
    details = []
    for module in discover_modules(root):
        build_file = root / module["build_file"] if module.get("build_file") else None
        text = read_text(build_file) if build_file else ""
        release_block = extract_release_block(text)

        compose_enabled = bool(
            re.search(r"buildFeatures\s*\{[^}]*compose\s*=\s*true", text, re.DOTALL)
            or "androidx.compose" in text
            or "composecompiler" in text.lower()
        )

        details.append(
            {
                "name": module["name"],
                "kind": module["kind"],
                "build_file": module["build_file"],
                "plugins": extract_plugins(text),
                "compile_sdk": match_int(text, r"compileSdk\s*=?\s*(\d+)"),
                "target_sdk": match_int(text, r"targetSdk\s*=?\s*(\d+)"),
                "min_sdk": match_int(text, r"minSdk\s*=?\s*(\d+)"),
                "compose_enabled": compose_enabled,
                "uses_kapt": bool(re.search(r'kotlin-kapt|kotlin\("kapt"\)|\bkapt\s*\(', text)),
                "uses_ksp": bool(re.search(r"com\.google\.devtools\.ksp|devtools\.ksp|\bksp\s*\(", text)),
                "release": {
                    "minify_enabled": match_bool(release_block, r"minifyEnabled\s*=?\s*(true|false)"),
                    "shrink_resources": match_bool(release_block, r"shrinkResources\s*=?\s*(true|false)"),
                },
            }
        )

    return details


def first_non_null(modules: list[dict], key: str, preferred_kinds: tuple[str, ...]) -> int | None:
    for preferred_kind in preferred_kinds:
        for module in modules:
            if module["kind"] == preferred_kind and module.get(key) is not None:
                return module[key]
    for module in modules:
        if module.get(key) is not None:
            return module[key]
    return None


def get_gradle_version(root: Path) -> str | None:
    props = root / "gradle" / "wrapper" / "gradle-wrapper.properties"
    text = read_text(props)
    match = re.search(r"gradle-(\d+\.\d+(?:\.\d+)?)", text)
    return match.group(1) if match else None


def resolve_version_ref(versions: dict, value) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        ref = value.get("ref")
        if ref:
            return versions.get(ref)
        return value.get("version")
    return None


def get_agp_version(catalog: dict, root: Path) -> str | None:
    versions = catalog.get("versions", {})
    for key in ("agp", "androidGradlePlugin", "android-gradle-plugin"):
        if key in versions:
            return resolve_version_ref(versions, versions[key])

    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file)
        match = re.search(r'com\.android\.tools\.build:gradle:(\S+)', text)
        if match:
            return match.group(1).strip("\"'")
    return None


def get_kotlin_version(catalog: dict, root: Path) -> str | None:
    versions = catalog.get("versions", {})
    for key in ("kotlin", "kotlinVersion"):
        if key in versions:
            return resolve_version_ref(versions, versions[key])

    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file)
        match = re.search(r'org\.jetbrains\.kotlin[^"\']*["\']\s*version\s*["\']([^"\']+)', text)
        if match:
            return match.group(1)
    return None


def get_compose_bom_version(catalog: dict) -> str | None:
    versions = catalog.get("versions", {})
    libs = catalog.get("libraries", {})
    for key, value in libs.items():
        if "compose-bom" not in key and "composeBom" not in key:
            continue
        if isinstance(value, dict):
            version = value.get("version")
            resolved = resolve_version_ref(versions, version)
            if resolved:
                return resolved
            module = value.get("module", "")
            if "compose-bom" in module:
                parts = module.split(":")
                if len(parts) >= 3:
                    return parts[-1]
        elif isinstance(value, str) and "compose-bom" in value:
            parts = value.split(":")
            if len(parts) >= 3:
                return parts[-1]
    return None


def parse_gradle_properties(root: Path) -> dict:
    props_path = root / "gradle.properties"
    text = read_text(props_path)

    values = {}
    for key in (
        "org.gradle.caching",
        "org.gradle.parallel",
        "org.gradle.configureondemand",
        "org.gradle.configuration-cache",
        "android.nonTransitiveRClass",
        "android.enableR8.fullMode",
    ):
        match = re.search(rf"^{re.escape(key)}\s*=\s*(.+)$", text, re.MULTILINE)
        if match:
            values[key] = match.group(1).strip()
    return values


def analyze(root: Path) -> dict:
    catalog = parse_version_catalog(root)
    modules = module_details(root)
    properties = parse_gradle_properties(root)

    app_modules = [module for module in modules if module["kind"] == "application"]
    library_modules = [module for module in modules if module["kind"] == "library"]
    aggregate_modules = app_modules or library_modules or modules

    return {
        "compile_sdk": first_non_null(aggregate_modules, "compile_sdk", ("application", "library")),
        "target_sdk": first_non_null(aggregate_modules, "target_sdk", ("application", "library")),
        "min_sdk": first_non_null(aggregate_modules, "min_sdk", ("application", "library")),
        "agp_version": get_agp_version(catalog, root),
        "gradle_version": get_gradle_version(root),
        "kotlin_version": get_kotlin_version(catalog, root),
        "compose_bom_version": get_compose_bom_version(catalog),
        "version_catalog_entries": sum(len(catalog.get(section, {})) for section in ("versions", "libraries", "plugins", "bundles")),
        "application_modules": [module["name"] for module in app_modules],
        "library_modules": [module["name"] for module in library_modules],
        "compose_enabled": any(module["compose_enabled"] for module in aggregate_modules),
        "uses_kapt": any(module["uses_kapt"] for module in modules),
        "uses_ksp": any(module["uses_ksp"] for module in modules),
        "module_builds": modules,
        "gradle_properties": properties,
        "limitations": [
            "Gradle parsing is static and file-based.",
            "Convention plugins and generated build logic are only partially visible without the Gradle model.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze Gradle build configuration")
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
