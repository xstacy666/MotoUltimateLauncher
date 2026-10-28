#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:?Usage: prepare_resource_build.sh <decoded-project-root>}"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
replacements = {
    "res/values/dimens.xml": {
        "@android:dimen/config_wearMaterial3_buttonCornerRadius": "4.0dp",
        "@android:dimen/navigation_bar_height": "24.0dp",
    },
    "res/values/styles.xml": {
        "@android:color/accent_device_default_light": "@color/accent_material_light",
    },
    "res/values-night/styles.xml": {
        "@android:color/accent_device_default_dark": "@color/accent_material_dark",
    },
    "res/layout/taskbar_divider_popup_menu.xml": {
        "@android:string/config_carrierAppInstallDialogComponent": "sans-serif",
    },
}
for rel, pairs in replacements.items():
    path = root / rel
    text = path.read_text(encoding="utf-8")
    for old, new in pairs.items():
        if old not in text:
            raise SystemExit(f"Expected framework reference not found: {rel}: {old}")
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

remaining = []
for path in (root / "res").rglob("*.xml"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    for marker in (
        "@android:dimen/config_wearMaterial3_buttonCornerRadius",
        "@android:dimen/navigation_bar_height",
        "@android:color/accent_device_default_light",
        "@android:color/accent_device_default_dark",
        "@android:string/config_carrierAppInstallDialogComponent",
    ):
        if marker in text:
            remaining.append(f"{path}: {marker}")
if remaining:
    raise SystemExit("Unresolved private Android framework references:\n" + "\n".join(remaining))
print("Patched four Android private-framework resource references for SDK-independent linking.")
PY

# The OEM settings initializer assumes every Preference has a non-null key.
python3 "$(dirname "$0")/fix_settings_null_keys.py" "$ROOT"
