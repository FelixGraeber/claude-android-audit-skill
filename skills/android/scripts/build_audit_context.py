#!/usr/bin/env python3
"""Build the shared audit context consumed by the Android audit skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import analyze_compose  # noqa: E402
import analyze_dependencies  # noqa: E402
import analyze_gradle  # noqa: E402
import analyze_manifest  # noqa: E402
import check_r8_config  # noqa: E402
import scan_project  # noqa: E402


def classify_project(scan: dict, gradle: dict) -> dict:
    app_modules = scan["module_counts"]["application"]
    library_modules = scan["module_counts"]["library"]
    total_modules = scan["module_counts"]["total"]
    compose_files = scan["source_counts"]["compose_files"]
    xml_layouts = scan["source_counts"]["xml_layouts"]

    if app_modules == 0 and library_modules > 0:
        repo_kind = "sdk-library"
    else:
        repo_kind = "application"

    app_shape = "multi-module" if total_modules > 1 else "single-module"
    if repo_kind == "sdk-library":
        app_shape = "library-only"

    if compose_files > 0 and xml_layouts == 0:
        ui_stack = "compose-first"
    elif compose_files == 0 and xml_layouts > 0:
        ui_stack = "xml-legacy"
    elif compose_files > 0 and xml_layouts > 0:
        ui_stack = "hybrid"
    else:
        ui_stack = "unknown"

    return {
        "repo_kind": repo_kind,
        "app_shape": app_shape,
        "ui_stack": ui_stack,
        "compose_enabled": gradle.get("compose_enabled", False),
    }


def grep_count(root: Path, pattern: str, suffixes: tuple[str, ...], source_set_only: bool = True) -> int:
    compiled = re.compile(pattern)
    count = 0
    for suffix in suffixes:
        for path in root.rglob(f"*{suffix}"):
            if "build" in path.parts or ".gradle" in path.parts:
                continue
            if source_set_only and ("src" not in path.parts or "main" not in path.parts):
                continue
            count += len(compiled.findall(path.read_text(errors="ignore")))
    return count


def build_context(root: Path) -> dict:
    scan = scan_project.scan(root)
    gradle = analyze_gradle.analyze(root)
    manifest = analyze_manifest.analyze(root)
    compose = analyze_compose.analyze(root, "all")
    dependencies = analyze_dependencies.analyze(root)
    r8 = check_r8_config.analyze(root)
    rules = json.loads((SKILL_DIR / "rules" / "rules.json").read_text())

    compat = {
        "uses_on_back_pressed": grep_count(root, r"\bonBackPressed\s*\(", (".kt", ".java")) > 0,
        "edge_to_edge_signal": grep_count(
            root,
            r"enableEdgeToEdge\s*\(|WindowCompat\.setDecorFitsSystemWindows\s*\(",
            (".kt", ".java"),
        ) > 0,
    }

    security = {
        "hardcoded_secrets_count": grep_count(
            root,
            r'(?i)(api[_-]?key|secret|password|token)\s*=\s*"[^"]+"',
            (".kt", ".java", ".properties", ".xml"),
            source_set_only=False,
        ),
        "webview_ssl_proceed_count": grep_count(root, r"\.proceed\s*\(", (".kt", ".java")),
    }

    return {
        "schema_version": "0.6.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "project_type": classify_project(scan, gradle),
        "scan": scan,
        "gradle": gradle,
        "manifest": manifest,
        "compose": compose,
        "dependencies": dependencies,
        "r8": r8,
        "compat": compat,
        "security": security,
        "rules": {
            "path": str(SKILL_DIR / "rules" / "rules.json"),
            "version": rules["version"],
        },
        "limitations": [
            "This context is static source evidence only.",
            "Merged manifest, Gradle model, screenshots, vitals, and store-console artifacts are not yet ingested.",
            "Accessibility and design findings should be treated as preflight evidence until runtime artifacts are available.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Build shared Android audit context")
    parser.add_argument("path", help="Path to project root")
    parser.add_argument("--output", help="Optional JSON output file")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(json.dumps({"error": f"Not a directory: {root}"}), file=sys.stderr)
        sys.exit(1)

    context = build_context(root)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(context, indent=2))

    if args.json or not args.output:
        print(json.dumps(context, indent=2))


if __name__ == "__main__":
    main()
