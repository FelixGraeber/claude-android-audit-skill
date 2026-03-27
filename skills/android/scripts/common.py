#!/usr/bin/env python3
"""Shared helpers for Android audit scripts."""

from __future__ import annotations

import re
from pathlib import Path

try:
    import tomli
except ImportError:
    try:
        import tomllib as tomli
    except ImportError:
        tomli = None


GRADLE_FILENAMES = ("build.gradle.kts", "build.gradle")
SETTINGS_FILENAMES = ("settings.gradle.kts", "settings.gradle")


def is_generated_path(path: Path) -> bool:
    return "build" in path.parts or ".gradle" in path.parts


def read_text(path: Path) -> str:
    try:
        return path.read_text(errors="ignore")
    except OSError:
        return ""


def parse_version_catalog(root: Path) -> dict:
    catalog_path = root / "gradle" / "libs.versions.toml"
    if not catalog_path.exists() or tomli is None:
        return {}
    try:
        with open(catalog_path, "rb") as handle:
            return tomli.load(handle)
    except Exception:
        return {}


def iter_gradle_build_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for filename in GRADLE_FILENAMES:
        for path in root.rglob(filename):
            if not is_generated_path(path):
                files.append(path)
    return sorted(set(files))


def relpath(root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(root.resolve()))


def production_source_files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    files: list[Path] = []
    for suffix in suffixes:
        for path in root.rglob(f"*{suffix}"):
            if is_generated_path(path):
                continue
            if "src" not in path.parts or "main" not in path.parts:
                continue
            files.append(path)
    return sorted(files)


def count_production_source_files(root: Path, suffix: str) -> int:
    return len(production_source_files(root, (suffix,)))


def count_xml_layouts(root: Path) -> int:
    count = 0
    for path in production_source_files(root, (".xml",)):
        if "res" in path.parts and any(part.startswith("layout") for part in path.parts):
            count += 1
    return count


def count_compose_files(root: Path) -> int:
    count = 0
    for path in production_source_files(root, (".kt",)):
        if "@Composable" in read_text(path):
            count += 1
    return count


def parse_settings_modules(root: Path) -> list[str]:
    modules: list[str] = []
    for filename in SETTINGS_FILENAMES:
        settings_file = root / filename
        if not settings_file.exists():
            continue

        text = read_text(settings_file)
        for args in re.findall(r"include\s*\((.*?)\)", text, re.DOTALL):
            for match in re.findall(r'["\'](:?[^"\']+)["\']', args):
                modules.append(normalize_module_name(match))

        for match in re.findall(r"include\s+['\"](:?[^'\"]+)['\"]", text):
            modules.append(normalize_module_name(match))

        break

    return sorted({module for module in modules if module})


def normalize_module_name(name: str) -> str:
    return name.strip().lstrip(":").replace(":", "/")


def module_name_for_build_file(root: Path, build_file: Path) -> str:
    module_dir = build_file.parent
    if module_dir == root:
        return "."
    return relpath(root, module_dir)


def find_module_build_file(root: Path, module_name: str) -> Path | None:
    module_dir = root if module_name == "." else root / module_name
    for filename in GRADLE_FILENAMES:
        candidate = module_dir / filename
        if candidate.exists():
            return candidate
    return None


def detect_module_kind(build_text: str) -> str:
    lowered = build_text.lower()
    if "com.android.application" in lowered:
        return "application"
    if "com.android.dynamic-feature" in lowered:
        return "dynamic-feature"
    if "com.android.test" in lowered:
        return "test"
    if "com.android.library" in lowered:
        return "library"
    return "unknown"


def discover_modules(root: Path) -> list[dict]:
    names = parse_settings_modules(root)

    build_files = iter_gradle_build_files(root)
    discovered_from_builds = {module_name_for_build_file(root, build_file) for build_file in build_files}
    names = sorted(set(names) | discovered_from_builds)

    modules: list[dict] = []
    for name in names:
        build_file = find_module_build_file(root, name)
        build_text = read_text(build_file) if build_file else ""
        modules.append(
            {
                "name": name,
                "build_file": relpath(root, build_file) if build_file else None,
                "kind": detect_module_kind(build_text),
            }
        )

    return modules


def extract_quoted_strings(value: str) -> list[str]:
    return re.findall(r'["\']([^"\']+)["\']', value)
