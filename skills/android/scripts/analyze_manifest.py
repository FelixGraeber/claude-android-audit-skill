#!/usr/bin/env python3
"""Parse AndroidManifest.xml files for permissions, components, and security config."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from common import discover_modules, relpath  # noqa: E402

try:
    from lxml import etree
except ImportError:
    etree = None

ANDROID_NS = "http://schemas.android.com/apk/res/android"


def ns(attr: str) -> str:
    return f"{{{ANDROID_NS}}}{attr}"


def module_manifest_paths(root: Path) -> list[dict]:
    manifests = []
    for module in discover_modules(root):
        if module["name"] == ".":
            candidates = [root / "src" / "main" / "AndroidManifest.xml", root / "AndroidManifest.xml"]
        else:
            candidates = [root / module["name"] / "src" / "main" / "AndroidManifest.xml"]

        for candidate in candidates:
            if candidate.exists():
                manifests.append({"module": module["name"], "kind": module["kind"], "path": candidate})
                break

    if not manifests:
        for path in root.rglob("AndroidManifest.xml"):
            if "build" in path.parts or ".gradle" in path.parts:
                continue
            manifests.append({"module": None, "kind": "unknown", "path": path})

    return manifests


def parse_manifest(root: Path, path: Path, module_name: str | None, module_kind: str) -> dict:
    try:
        tree = etree.parse(str(path))
    except Exception as exc:
        return {"path": relpath(root, path), "module": module_name, "kind": module_kind, "error": str(exc)}

    root_el = tree.getroot()
    permissions = []
    uses_permission_sdk_23 = []

    for tag in ("uses-permission", "uses-permission-sdk-23"):
        for perm in root_el.findall(tag):
            name = perm.get(ns("name"))
            if not name:
                continue
            if tag == "uses-permission":
                permissions.append(name)
            else:
                uses_permission_sdk_23.append(name)

    app = root_el.find("application")
    component_counts = {"activities": 0, "services": 0, "receivers": 0, "providers": 0}
    exported_components = []
    foreground_service_types = []

    app_data = {
        "uses_cleartext": None,
        "network_security_config": None,
        "enable_on_back_invoked_callback": None,
        "allow_backup": None,
        "debuggable": None,
        "data_extraction_rules": None,
    }

    if app is not None:
        app_data.update(
            {
                "uses_cleartext": app.get(ns("usesCleartextTraffic")),
                "network_security_config": app.get(ns("networkSecurityConfig")),
                "enable_on_back_invoked_callback": app.get(ns("enableOnBackInvokedCallback")),
                "allow_backup": app.get(ns("allowBackup")),
                "debuggable": app.get(ns("debuggable")),
                "data_extraction_rules": app.get(ns("dataExtractionRules")),
            }
        )

        tag_map = {
            "activity": "activities",
            "service": "services",
            "receiver": "receivers",
            "provider": "providers",
        }
        for tag, count_key in tag_map.items():
            for element in app.findall(tag):
                component_counts[count_key] += 1
                exported = element.get(ns("exported"))
                has_intent_filter = len(element.findall("intent-filter")) > 0
                permission = element.get(ns("permission"))
                if tag == "service":
                    value = element.get(ns("foregroundServiceType"))
                    if value:
                        for service_type in value.split("|"):
                            service_type = service_type.strip()
                            if service_type:
                                foreground_service_types.append(service_type)

                inferred_exported = None
                if exported is not None:
                    inferred_exported = exported.lower() == "true"
                elif has_intent_filter:
                    inferred_exported = True

                if inferred_exported:
                    exported_components.append(
                        {
                            "name": element.get(ns("name")),
                            "type": tag,
                            "has_intent_filter": has_intent_filter,
                            "has_permission": permission is not None,
                            "permission": permission,
                            "manifest": relpath(root, path),
                        }
                    )

    queries_count = len(root_el.findall("queries"))

    return {
        "path": relpath(root, path),
        "module": module_name,
        "kind": module_kind,
        "permissions": sorted(set(permissions)),
        "uses_permission_sdk_23": sorted(set(uses_permission_sdk_23)),
        "exported_components": exported_components,
        "foreground_service_types": sorted(set(foreground_service_types)),
        "component_counts": component_counts,
        "queries_count": queries_count,
        **app_data,
    }


def bool_string(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == "true"


def analyze(root: Path) -> dict:
    if etree is None:
        print(json.dumps({"error": "lxml not installed. Run: uv pip install lxml"}), file=sys.stderr)
        sys.exit(1)

    manifests = [
        parse_manifest(root, entry["path"], entry["module"], entry["kind"])
        for entry in module_manifest_paths(root)
    ]

    valid_manifests = [manifest for manifest in manifests if "error" not in manifest]
    if not valid_manifests:
        return {
            "manifest_files": manifests,
            "permissions": [],
            "exported_components": [],
            "foreground_service_types": [],
            "component_counts": {"activities": 0, "services": 0, "receivers": 0, "providers": 0},
            "limitations": [
                "No parseable manifest found.",
                "Merged manifest inspection is not yet implemented.",
            ],
        }

    preferred = next(
        (manifest for manifest in valid_manifests if manifest["kind"] == "application"),
        valid_manifests[0],
    )

    combined_counts = {"activities": 0, "services": 0, "receivers": 0, "providers": 0}
    for manifest in valid_manifests:
        for key in combined_counts:
            combined_counts[key] += manifest["component_counts"].get(key, 0)

    return {
        "manifest_files": manifests,
        "primary_manifest": preferred["path"],
        "permissions": sorted({perm for manifest in valid_manifests for perm in manifest["permissions"]}),
        "uses_permission_sdk_23": sorted({perm for manifest in valid_manifests for perm in manifest["uses_permission_sdk_23"]}),
        "exported_components": [component for manifest in valid_manifests for component in manifest["exported_components"]],
        "foreground_service_types": sorted(
            {service_type for manifest in valid_manifests for service_type in manifest["foreground_service_types"]}
        ),
        "uses_cleartext": bool_string(preferred.get("uses_cleartext")),
        "has_network_security_config": bool(preferred.get("network_security_config")),
        "enable_on_back_invoked_callback": preferred.get("enable_on_back_invoked_callback"),
        "allow_backup": bool_string(preferred.get("allow_backup")),
        "debuggable": bool_string(preferred.get("debuggable")),
        "data_extraction_rules": preferred.get("data_extraction_rules"),
        "queries_count": sum(manifest.get("queries_count", 0) for manifest in valid_manifests),
        "component_counts": combined_counts,
        "limitations": [
            "Manifest analysis is based on source manifests, not the merged manifest.",
            "Type-specific foreground service permission matching still requires AGP merged-manifest evidence.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze AndroidManifest.xml files")
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
