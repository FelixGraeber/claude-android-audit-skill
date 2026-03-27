from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skills.android.scripts import analyze_compose, build_audit_context, score

REPO_ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = REPO_ROOT / "skills" / "android" / "rules" / "rules.json"


class AuditPipelineTests(unittest.TestCase):
    def test_compose_null_content_description_is_decorative(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            file_path = root / "app" / "src" / "main" / "kotlin" / "Example.kt"
            file_path.parent.mkdir(parents=True)
            file_path.write_text(
                """
                import androidx.compose.material3.Icon
                import androidx.compose.runtime.Composable

                @Composable
                fun Example() {
                    Icon(Icons.Default.Home, contentDescription = null)
                }
                """
            )

            result = analyze_compose.analyze(root, "accessibility")
            accessibility = result["accessibility"]

            self.assertEqual(accessibility["content_descriptions_missing"], 0)
            self.assertEqual(accessibility["decorative_content_descriptions"], 1)

    @unittest.skipUnless(build_audit_context.analyze_manifest.etree is not None, "lxml required")
    def test_library_only_project_classifies_as_sdk_library(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "settings.gradle.kts").write_text('include(":sdk")\n')
            (root / "sdk" / "build.gradle.kts").parent.mkdir(parents=True)
            (root / "sdk" / "build.gradle.kts").write_text(
                """
                plugins {
                    id("com.android.library")
                    kotlin("android")
                }

                android {
                    namespace = "com.example.sdk"
                    compileSdk = 35
                    defaultConfig {
                        minSdk = 24
                    }
                }
                """
            )
            (root / "sdk" / "src" / "main").mkdir(parents=True)
            (root / "sdk" / "src" / "main" / "AndroidManifest.xml").write_text(
                """
                <manifest package="com.example.sdk" xmlns:android="http://schemas.android.com/apk/res/android">
                    <application />
                </manifest>
                """
            )

            context = build_audit_context.build_context(root)
            self.assertEqual(context["project_type"]["repo_kind"], "sdk-library")
            self.assertEqual(context["project_type"]["app_shape"], "library-only")
            self.assertIsNone(context["r8"]["all_application_release_variants_protected"])

    def test_score_caps_without_category_scores(self):
        context = {
            "rules": {
                "path": str(RULES_PATH)
            },
            "manifest": {
                "exported_components": [],
                "uses_cleartext": True,
                "has_network_security_config": False,
                "debuggable": False
            },
            "gradle": {
                "target_sdk": 34,
                "uses_kapt": True
            },
            "scan": {
                "has_benchmark_module": False
            },
            "compose": {
                "accessibility": {
                    "small_touch_target_warnings": 1
                }
            },
            "dependencies": {
                "deprecated_deps": []
            },
            "compat": {
                "edge_to_edge_signal": False,
                "uses_on_back_pressed": True
            },
            "security": {
                "hardcoded_secrets_count": 0,
                "webview_ssl_proceed_count": 0
            },
            "r8": {
                "all_application_release_variants_protected": False
            }
        }

        rules = json.loads(Path(context["rules"]["path"]).read_text())
        result = score.evaluate(context, rules, None)

        self.assertEqual(result["status"], "insufficient_evidence_for_final_score")
        self.assertTrue(any(cap["id"] == "critical-cap" for cap in result["score_caps_applied"]))

    def test_score_rejects_partial_category_scores(self):
        context = {
            "rules": {
                "path": str(RULES_PATH)
            },
            "manifest": {
                "exported_components": [],
                "uses_cleartext": False,
                "has_network_security_config": True,
                "debuggable": False
            },
            "gradle": {
                "target_sdk": 35,
                "uses_kapt": False
            },
            "scan": {
                "has_benchmark_module": True
            },
            "compose": {
                "accessibility": {
                    "small_touch_target_warnings": 0
                }
            },
            "dependencies": {
                "deprecated_deps": []
            },
            "compat": {
                "edge_to_edge_signal": True,
                "uses_on_back_pressed": False
            },
            "security": {
                "hardcoded_secrets_count": 0,
                "webview_ssl_proceed_count": 0
            },
            "r8": {
                "all_application_release_variants_protected": True
            }
        }

        rules = json.loads(RULES_PATH.read_text())
        result = score.evaluate(
            context,
            rules,
            {
                "architecture": 80,
                "security": 90
            },
        )

        self.assertEqual(result["status"], "insufficient_evidence_for_final_score")
        self.assertIn("performance", result["missing_categories"])

    def test_library_only_repo_does_not_trigger_release_r8_gate(self):
        context = {
            "manifest": {
                "exported_components": [],
                "uses_cleartext": False,
                "has_network_security_config": True,
                "debuggable": False
            },
            "gradle": {
                "target_sdk": None,
                "uses_kapt": False
            },
            "scan": {
                "has_benchmark_module": True
            },
            "compose": {
                "accessibility": {
                    "small_touch_target_warnings": 0
                }
            },
            "dependencies": {
                "deprecated_deps": []
            },
            "compat": {
                "edge_to_edge_signal": True,
                "uses_on_back_pressed": False
            },
            "security": {
                "hardcoded_secrets_count": 0,
                "webview_ssl_proceed_count": 0
            },
            "r8": {
                "application_release_variants_evaluated": 0,
                "all_application_release_variants_protected": None
            }
        }

        rules = json.loads(RULES_PATH.read_text())
        c7 = next(gate for gate in rules["gates"] if gate["id"] == "C7")
        _evidence_key, result = score.evaluate_gate(c7, context)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
