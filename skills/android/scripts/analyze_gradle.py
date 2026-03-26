#!/usr/bin/env python3
"""Parse Android build configuration from Gradle files."""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli
    except ImportError:
        tomli = None


def parse_version_catalog(root: Path) -> dict:
    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists() or tomli is None:
        return {}
    try:
        with open(catalog_path, "rb") as f:
            return tomli.load(f)
    except Exception:
        return {}


def extract_sdk_values(root: Path) -> dict:
    result = {"compile_sdk": None, "target_sdk": None, "min_sdk": None, "minify_enabled": None, "shrink_resources": None}
    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts or "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue
            for key, pattern in [
                ("compile_sdk", r"compileSdk\s*=?\s*(\d+)"),
                ("target_sdk", r"targetSdk\s*=?\s*(\d+)"),
                ("min_sdk", r"minSdk\s*=?\s*(\d+)"),
            ]:
                if result[key] is None:
                    m = re.search(pattern, text)
                    if m:
                        result[key] = int(m.group(1))
            if result["minify_enabled"] is None:
                m = re.search(r"minifyEnabled\s*=?\s*(true|false)", text, re.IGNORECASE)
                if m:
                    result["minify_enabled"] = m.group(1).lower() == "true"
            if result["shrink_resources"] is None:
                m = re.search(r"shrinkResources\s*=?\s*(true|false)", text, re.IGNORECASE)
                if m:
                    result["shrink_resources"] = m.group(1).lower() == "true"
    return result


def detect_plugins(root: Path) -> dict:
    plugins = set()
    uses_kapt = False
    uses_ksp = False
    compose_enabled = False

    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts or "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue
            for m in re.findall(r'id\s*\(\s*["\']([^"\']+)["\']\s*\)', text):
                plugins.add(m)
            for m in re.findall(r'alias\s*\(\s*libs\.plugins\.([^)]+)\s*\)', text):
                plugins.add(m.replace(".", "-"))
            if re.search(r'kotlin-kapt|kotlin\("kapt"\)', text):
                uses_kapt = True
            if re.search(r'com\.google\.devtools\.ksp|devtools\.ksp', text):
                uses_ksp = True
            if re.search(r'compose\s*=\s*true|buildFeatures\s*\{[^}]*compose\s*=\s*true', text, re.DOTALL):
                compose_enabled = True
            if "composeOptions" in text or "compose" in text.lower():
                compose_enabled = True

    detected = []
    plugin_keywords = {
        "kotlin-android": "kotlin-android",
        "ksp": "ksp",
        "hilt": "hilt",
        "room": "room",
        "compose": "compose",
        "kapt": "kapt",
        "serialization": "kotlin-serialization",
    }
    for keyword, name in plugin_keywords.items():
        if any(keyword in p for p in plugins):
            detected.append(name)
    return {"plugins": sorted(set(detected)), "uses_kapt": uses_kapt, "uses_ksp": uses_ksp, "compose_enabled": compose_enabled}


def get_gradle_version(root: Path) -> str | None:
    props = root / "gradle" / "wrapper" / "gradle-wrapper.properties"
    if not props.exists():
        return None
    try:
        text = props.read_text(errors="ignore")
        m = re.search(r"gradle-(\d+\.\d+(?:\.\d+)?)", text)
        return m.group(1) if m else None
    except OSError:
        return None


def get_agp_version(catalog: dict, root: Path) -> str | None:
    versions = catalog.get("versions", {})
    for key in ("agp", "androidGradlePlugin", "android-gradle-plugin"):
        if key in versions:
            v = versions[key]
            return v if isinstance(v, str) else v.get("version", str(v))

    for name in ("build.gradle.kts", "build.gradle"):
        build_file = root / name
        if build_file.exists():
            try:
                text = build_file.read_text(errors="ignore")
                m = re.search(r'com\.android\.tools\.build:gradle:(\S+)', text)
                if m:
                    return m.group(1).strip("\"'")
                m = re.search(r'com\.android\.\w+["\s]+version\s+["\'](\S+)', text)
                if m:
                    return m.group(1)
            except OSError:
                continue
    return None


def get_compose_bom_version(catalog: dict) -> str | None:
    libs = catalog.get("libraries", {})
    for key, val in libs.items():
        if "compose-bom" in key or "composeBom" in key:
            if isinstance(val, dict):
                module = val.get("module", "") or val.get("group", "")
                if "compose-bom" in module or "compose.bom" in module:
                    version = val.get("version", {})
                    if isinstance(version, dict):
                        ref = version.get("ref", "")
                        versions = catalog.get("versions", {})
                        return versions.get(ref, ref) if ref else None
                    return str(version) if version else None
            elif isinstance(val, str) and "compose-bom" in val:
                parts = val.split(":")
                return parts[-1] if len(parts) >= 3 else None
    return None


def analyze(root: Path) -> dict:
    catalog = parse_version_catalog(root)
    sdk = extract_sdk_values(root)
    plugin_info = detect_plugins(root)
    gradle_version = get_gradle_version(root)
    agp_version = get_agp_version(catalog, root)
    compose_bom = get_compose_bom_version(catalog)

    catalog_entries = 0
    for section in ("versions", "libraries", "plugins", "bundles"):
        catalog_entries += len(catalog.get(section, {}))

    return {
        "target_sdk": sdk["target_sdk"],
        "compile_sdk": sdk["compile_sdk"],
        "min_sdk": sdk["min_sdk"],
        "agp_version": agp_version,
        "gradle_version": gradle_version,
        "plugins": plugin_info["plugins"],
        "uses_kapt": plugin_info["uses_kapt"],
        "uses_ksp": plugin_info["uses_ksp"],
        "minify_enabled": sdk["minify_enabled"],
        "shrink_resources": sdk["shrink_resources"],
        "compose_enabled": plugin_info["compose_enabled"],
        "compose_bom_version": compose_bom,
        "version_catalog_entries": catalog_entries,
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
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
