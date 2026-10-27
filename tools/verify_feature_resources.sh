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
for name in mod_icon_shape mod_icon_pack mod_icon_zoom mod_icon_inset "Icon pack" "Icon foreground zoom" "Icon safe-zone padding" "Icon Lab" "Dock Studio"; do
  grep -q "$name" "$TMP/preferences.txt" || { echo "Missing preference entry: $name" >&2; exit 1; }
done
# The icon-pack selector must remain the real package-discovery ListPreference,
# not a duplicate free-text field that never validates installed pack packages.
grep -q "ModIconPackPreference" "$TMP/preferences.txt" || {
  echo "Icon pack setting is not wired to ModIconPackPreference" >&2; exit 1;
}
unzip -p "$APK" AndroidManifest.xml | strings -el > "$TMP/manifest.txt"
for action in "org.adw.launcher.THEMES" "com.novalauncher.THEME" "com.anddoes.launcher.THEME" "org.adw.launcher.icons.ACTION_PICK_ICON"; do
  grep -q "$action" "$TMP/manifest.txt" || {
    echo "Missing Android package-visibility query for icon-pack action: $action" >&2; exit 1;
  }
done
echo "Verified: Icon Lab uses the real icon-pack picker, exposes legacy pack discovery actions, and packages shape/zoom/padding and Dock Studio preferences."
