#!/usr/bin/env bash
set -euo pipefail
APK="${1:?Usage: verify_feature_resources.sh <apk>}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
unzip -p "$APK" resources.arsc | strings > "$TMP/resources.txt"
unzip -p "$APK" res/xml/launcher_preferences.xml | strings > "$TMP/preferences.txt"
for name in mod_icon_shape_entries mod_icon_shape_values mod_icon_zoom_entries mod_icon_zoom_values mod_icon_inset_entries mod_icon_inset_values; do
  grep -q "$name" "$TMP/resources.txt" || { echo "Missing resource array: $name" >&2; exit 1; }
done
for name in mod_icon_shape mod_icon_zoom mod_icon_inset "Icon foreground zoom" "Icon safe-zone padding" "Icon Lab" "Dock Studio"; do
  grep -q "$name" "$TMP/preferences.txt" || { echo "Missing preference entry: $name" >&2; exit 1; }
done
echo "Verified: Icon Lab shape chooser and Dock Studio preferences are packaged."
