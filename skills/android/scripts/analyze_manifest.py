#!/usr/bin/env python3
"""Parse AndroidManifest.xml files for permissions, components, and security config."""

import argparse
import json
import sys
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    etree = None

ANDROID_NS = "http://schemas.android.com/apk/res/android"


def ns(attr: str) -> str:
    return f"{{{ANDROID_NS}}}{attr}"


def find_manifests(root: Path) -> list[Path]:
    manifests = []
    for p in root.rglob("AndroidManifest.xml"):
        if ".gradle" not in p.parts and "build" not in p.parts:
            manifests.append(p)
    return sorted(manifests)


def parse_manifest(path: Path) -> dict:
    try:
        tree = etree.parse(str(path))
    except Exception as e:
        return {"error": f"Failed to parse {path}: {e}"}

    root_el = tree.getroot()

    permissions = []
    for perm in root_el.findall("uses-permission"):
        name = perm.get(ns("name"))
        if name:
            permissions.append(name)

    exported_components = []
    component_counts = {"activities": 0, "services": 0, "receivers": 0, "providers": 0}
    foreground_service_types = []

    app = root_el.find("application")
    if app is None:
        return {
            "permissions": permissions,
            "exported_components": [],
            "foreground_service_types": [],
            "component_counts": component_counts,
        }

    uses_cleartext = app.get(ns("usesCleartextTraffic"))
    network_security_config = app.get(ns("networkSecurityConfig"))
    enable_on_back = app.get(ns("enableOnBackInvokedCallback"))

    tag_map = {
        "activity": "activities",
        "service": "services",
        "receiver": "receivers",
        "provider": "providers",
    }

    for tag, count_key in tag_map.items():
        for el in app.findall(tag):
            component_counts[count_key] += 1
            name = el.get(ns("name"), "")
            exported = el.get(ns("exported"))
            has_intent_filter = len(el.findall("intent-filter")) > 0
            permission = el.get(ns("permission"))

            if tag == "service":
                fst = el.get(ns("foregroundServiceType"))
                if fst:
                    for t in fst.split("|"):
                        t = t.strip()
                        if t and t not in foreground_service_types:
                            foreground_service_types.append(t)

            is_exported = None
            if exported is not None:
                is_exported = exported.lower() == "true"
            elif has_intent_filter:
                is_exported = True

            if is_exported:
                exported_components.append({
                    "name": name,
                    "type": tag,
                    "exported": True,
                    "has_intent_filter": has_intent_filter,
                    "has_permission": permission is not None,
                })

    return {
        "permissions": permissions,
        "exported_components": exported_components,
        "foreground_service_types": foreground_service_types,
        "uses_cleartext": uses_cleartext,
        "network_security_config": network_security_config,
        "enable_on_back": enable_on_back,
        "component_counts": component_counts,
    }


def analyze(root: Path) -> dict:
    if etree is None:
        print(json.dumps({"error": "lxml not installed. Run: uv pip install lxml"}), file=sys.stderr)
        sys.exit(1)

    manifests = find_manifests(root)
    if not manifests:
        return {
            "permissions": [],
            "exported_components": [],
            "foreground_service_types": [],
            "uses_cleartext": False,
            "has_network_security_config": False,
            "has_predictive_back": False,
            "enable_on_back_invoked": None,
            "component_counts": {"activities": 0, "services": 0, "receivers": 0, "providers": 0},
        }

    all_permissions = []
    all_exported = []
    all_fst = []
    uses_cleartext_val = None
    has_nsc = False
    enable_on_back_val = None
    total_counts = {"activities": 0, "services": 0, "receivers": 0, "providers": 0}

    for manifest in manifests:
        data = parse_manifest(manifest)
        if "error" in data:
            continue
        all_permissions.extend(data["permissions"])
        all_exported.extend(data["exported_components"])
        all_fst.extend(data["foreground_service_types"])
        for k in total_counts:
            total_counts[k] += data["component_counts"].get(k, 0)

        if data.get("uses_cleartext") is not None and uses_cleartext_val is None:
            uses_cleartext_val = data["uses_cleartext"]
        if data.get("network_security_config"):
            has_nsc = True
        if data.get("enable_on_back") is not None and enable_on_back_val is None:
            enable_on_back_val = data["enable_on_back"]

    cleartext = False
    if uses_cleartext_val is not None:
        cleartext = uses_cleartext_val.lower() == "true"

    has_predictive_back = enable_on_back_val is not None and enable_on_back_val.lower() == "true"

    return {
        "permissions": sorted(set(all_permissions)),
        "exported_components": all_exported,
        "foreground_service_types": sorted(set(all_fst)),
        "uses_cleartext": cleartext,
        "has_network_security_config": has_nsc,
        "has_predictive_back": has_predictive_back,
        "enable_on_back_invoked": enable_on_back_val,
        "component_counts": total_counts,
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
        for k, v in result.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()
