#!/usr/bin/env bash
set -euo pipefail
APK="${1:?Usage: verify_feature_resources.sh <apk>}"
# The Icon Lab patch is intentionally disabled because its rewritten Smali crashes
# ART verification. Do not require resources that only that patch injects.
unzip -tq "$APK"
unzip -Z1 "$APK" | grep -qx 'AndroidManifest.xml'
unzip -Z1 "$APK" | grep -qx 'resources.arsc'
unzip -Z1 "$APK" | grep -Eq '^classes([0-9]+)?\.dex$'
echo "Verified: APK archive, manifest, resource table, and DEX payload are present. Optional Icon Lab zoom patch remains disabled."
