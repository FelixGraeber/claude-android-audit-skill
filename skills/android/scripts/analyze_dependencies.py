#!/usr/bin/env python3
"""Check dependency health in Android projects."""

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

DEPRECATED_LIBS = {
    "androidx.security:security-crypto": {
        "name": "security-crypto",
        "reason": "EncryptedSharedPreferences deprecated, use DataStore + Tink",
    },
    "com.android.support": {
        "name": "android-support-library",
        "reason": "Migrate to AndroidX",
    },
}

DEPRECATED_PLUGINS = {
    "kotlin-android-extensions": {
        "name": "kotlin-android-extensions",
        "reason": "Deprecated, use View Binding or Jetpack Compose",
    },
}


def parse_version_catalog(root: Path) -> dict:
    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists() or tomli is None:
        return {}
    try:
        with open(catalog_path, "rb") as f:
            return tomli.load(f)
    except Exception:
        return {}


def check_deprecated_deps(catalog: dict) -> list[dict]:
    deprecated = []
    libs = catalog.get("libraries", {})
    for _key, val in libs.items():
        module = ""
        if isinstance(val, dict):
            module = val.get("module", "") or ""
            if not module:
                group = val.get("group", "")
                name = val.get("name", "")
                module = f"{group}:{name}" if group else name
        elif isinstance(val, str):
            module = val

        for dep_prefix, info in DEPRECATED_LIBS.items():
            if dep_prefix in module:
                deprecated.append(info)

    plugins = catalog.get("plugins", {})
    for _key, val in plugins.items():
        plugin_id = ""
        if isinstance(val, dict):
            plugin_id = val.get("id", "")
        elif isinstance(val, str):
            plugin_id = val
        for plugin_name, info in DEPRECATED_PLUGINS.items():
            if plugin_name in plugin_id:
                deprecated.append(info)

    return deprecated


def find_kapt_ksp_deps(root: Path) -> tuple[list[str], list[str]]:
    kapt_deps = []
    ksp_deps = []

    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts or "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue

            for m in re.findall(r'kapt\s*\(\s*(?:libs\.\w+[\w.]*|"[^"]+"|\'[^\']+\')\s*\)', text):
                dep_name = re.search(r'libs\.(\S+?)[\s)]|["\']([^"\']+)["\']', m)
                if dep_name:
                    name = dep_name.group(1) or dep_name.group(2)
                    name = name.replace(".", "-").split(":")[-1] if ":" in name else name
                    kapt_deps.append(name)

            for m in re.findall(r'ksp\s*\(\s*(?:libs\.\w+[\w.]*|"[^"]+"|\'[^\']+\')\s*\)', text):
                dep_name = re.search(r'libs\.(\S+?)[\s)]|["\']([^"\']+)["\']', m)
                if dep_name:
                    name = dep_name.group(1) or dep_name.group(2)
                    name = name.replace(".", "-").split(":")[-1] if ":" in name else name
                    ksp_deps.append(name)

    return sorted(set(kapt_deps)), sorted(set(ksp_deps))


def get_compose_bom_version(catalog: dict) -> str | None:
    libs = catalog.get("libraries", {})
    for key, val in libs.items():
        if "compose-bom" in key or "composeBom" in key:
            if isinstance(val, dict):
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


def count_inline_versions(root: Path) -> int:
    count = 0
    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts or "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue
            inline = re.findall(r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation|androidTestImplementation)\s*\(\s*"[^"]+:[^"]+:[^"]+"\s*\)', text)
            count += len(inline)
    return count


def check_tools(root: Path) -> dict:
    has_leak_canary = False
    has_strict_mode = False

    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts or "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue
            if "leakcanary" in text.lower():
                has_leak_canary = True

    for kt_file in root.rglob("*.kt"):
        if ".gradle" in kt_file.parts or "build" in kt_file.parts:
            continue
        try:
            text = kt_file.read_text(errors="ignore")
        except OSError:
            continue
        if "StrictMode" in text:
            has_strict_mode = True
            break

    if not has_strict_mode:
        for java_file in root.rglob("*.java"):
            if ".gradle" in java_file.parts or "build" in java_file.parts:
                continue
            try:
                text = java_file.read_text(errors="ignore")
            except OSError:
                continue
            if "StrictMode" in text:
                has_strict_mode = True
                break

    return {"has_leak_canary": has_leak_canary, "has_strict_mode": has_strict_mode}


def analyze(root: Path) -> dict:
    catalog = parse_version_catalog(root)

    catalog_entries = 0
    for section in ("versions", "libraries", "plugins", "bundles"):
        catalog_entries += len(catalog.get(section, {}))

    deprecated = check_deprecated_deps(catalog)

    for gradle_name in ("build.gradle.kts", "build.gradle"):
        for build_file in root.rglob(gradle_name):
            if ".gradle" in build_file.parts or "build" in build_file.parts:
                continue
            try:
                text = build_file.read_text(errors="ignore")
            except OSError:
                continue
            for plugin_name, info in DEPRECATED_PLUGINS.items():
                if plugin_name in text and info not in deprecated:
                    deprecated.append(info)
            for dep_prefix, info in DEPRECATED_LIBS.items():
                if dep_prefix in text and info not in deprecated:
                    deprecated.append(info)

    kapt_deps, ksp_deps = find_kapt_ksp_deps(root)
    compose_bom = get_compose_bom_version(catalog)
    inline_versions = count_inline_versions(root)
    tools = check_tools(root)

    return {
        "catalog_entries": catalog_entries,
        "inline_versions": inline_versions,
        "deprecated_deps": deprecated,
        "kapt_deps": kapt_deps,
        "ksp_deps": ksp_deps,
        "compose_bom_version": compose_bom,
        "has_leak_canary": tools["has_leak_canary"],
        "has_strict_mode": tools["has_strict_mode"],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze dependency health")
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
