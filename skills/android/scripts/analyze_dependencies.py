#!/usr/bin/env python3
"""Check dependency health in Android projects."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import iter_gradle_build_files, parse_version_catalog, read_text  # noqa: E402


DEPRECATED_LIBS = {
    "androidx.security:security-crypto": {
        "name": "security-crypto",
        "reason": "Deprecated in AndroidX Security 1.1.0; prefer app-specific storage design with platform keystore primitives.",
    },
    "com.android.support": {
        "name": "android-support-library",
        "reason": "Legacy support library; migrate to AndroidX.",
    },
}

DEPRECATED_PLUGINS = {
    "kotlin-android-extensions": {
        "name": "kotlin-android-extensions",
        "reason": "Deprecated; replace synthetic accessors with View Binding or Compose.",
    },
}


def check_deprecated_catalog_entries(catalog: dict) -> list[dict]:
    deprecated = []
    libraries = catalog.get("libraries", {})
    for value in libraries.values():
        module = ""
        if isinstance(value, dict):
            module = value.get("module", "")
            if not module:
                group = value.get("group", "")
                name = value.get("name", "")
                if group and name:
                    module = f"{group}:{name}"
        elif isinstance(value, str):
            module = value

        for prefix, info in DEPRECATED_LIBS.items():
            if prefix in module and info not in deprecated:
                deprecated.append(info)

    plugins = catalog.get("plugins", {})
    for value in plugins.values():
        plugin_id = value.get("id", "") if isinstance(value, dict) else str(value)
        for name, info in DEPRECATED_PLUGINS.items():
            if name in plugin_id and info not in deprecated:
                deprecated.append(info)
    return deprecated


def find_processor_deps(root: Path) -> tuple[list[str], list[str]]:
    kapt_deps = set()
    ksp_deps = set()
    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file)
        for config_name, target in (("kapt", kapt_deps), ("ksp", ksp_deps)):
            pattern = rf'{config_name}\s*\(\s*(libs\.[\w.]+|["\'][^"\']+["\'])\s*\)'
            for match in re.finditer(pattern, text):
                dep = match.group(1).strip("\"'")
                target.add(dep.replace(".", "-").split(":")[-1] if ":" in dep else dep)
    return sorted(kapt_deps), sorted(ksp_deps)


def count_inline_versions(root: Path) -> int:
    count = 0
    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file)
        inline = re.findall(
            r'(?:implementation|api|compileOnly|runtimeOnly|testImplementation|androidTestImplementation)\s*\(\s*"[^"]+:[^"]+:[^"]+"\s*\)',
            text,
        )
        count += len(inline)
    return count


def check_tools(root: Path) -> dict:
    has_leak_canary = False
    has_strict_mode = False

    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file).lower()
        if "leakcanary" in text:
            has_leak_canary = True

    for suffix in ("*.kt", "*.java"):
        for path in root.rglob(suffix):
            if "build" in path.parts or ".gradle" in path.parts:
                continue
            if "src" not in path.parts or "main" not in path.parts:
                continue
            if "StrictMode" in read_text(path):
                has_strict_mode = True
                break
        if has_strict_mode:
            break

    return {"has_leak_canary": has_leak_canary, "has_strict_mode": has_strict_mode}


def check_repository_hygiene(root: Path) -> dict:
    text = "\n".join(read_text(build_file) for build_file in iter_gradle_build_files(root))
    settings_text = read_text(root / "settings.gradle.kts") + "\n" + read_text(root / "settings.gradle")
    combined = f"{settings_text}\n{text}"

    repo_urls = re.findall(r"url\s*=\s*uri\s*\(\s*[\"']([^\"']+)[\"']\s*\)", combined)
    repo_urls += re.findall(r"maven\s*\(\s*[\"']([^\"']+)[\"']\s*\)", combined)

    return {
        "uses_jcenter": "jcenter()" in combined,
        "uses_maven_local": "mavenLocal()" in combined,
        "custom_repositories": sorted(set(repo_urls)),
        "has_dependency_verification": (root / "gradle" / "verification-metadata.xml").exists(),
    }


def check_version_risks(root: Path) -> dict:
    snapshots = []
    wildcards = []
    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file)
        snapshots.extend(re.findall(r'["\'][^"\']+:[^"\']+:[^"\']*SNAPSHOT[^"\']*["\']', text))
        wildcards.extend(re.findall(r'["\'][^"\']+:[^"\']+:\+[^"\']*["\']', text))
    return {
        "snapshot_dependencies": sorted(set(snapshots)),
        "wildcard_dependencies": sorted(set(wildcards)),
    }


def analyze(root: Path) -> dict:
    catalog = parse_version_catalog(root)
    deprecated = check_deprecated_catalog_entries(catalog)

    for build_file in iter_gradle_build_files(root):
        text = read_text(build_file)
        for plugin_name, info in DEPRECATED_PLUGINS.items():
            if plugin_name in text and info not in deprecated:
                deprecated.append(info)
        for dep_prefix, info in DEPRECATED_LIBS.items():
            if dep_prefix in text and info not in deprecated:
                deprecated.append(info)

    kapt_deps, ksp_deps = find_processor_deps(root)
    tools = check_tools(root)
    repos = check_repository_hygiene(root)
    version_risks = check_version_risks(root)

    return {
        "catalog_entries": sum(len(catalog.get(section, {})) for section in ("versions", "libraries", "plugins", "bundles")),
        "inline_versions": count_inline_versions(root),
        "deprecated_deps": deprecated,
        "kapt_deps": kapt_deps,
        "ksp_deps": ksp_deps,
        "has_leak_canary": tools["has_leak_canary"],
        "has_strict_mode": tools["has_strict_mode"],
        **repos,
        **version_risks,
        "limitations": [
            "Dependency analysis is static and does not resolve transitive graphs.",
            "Version freshness still requires an external lookup layer.",
        ],
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
        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
