#!/usr/bin/env bash
# Safe, non-destructive preparation for Moto Launcher Ultimate.
# This script does not patch, sign, install, or overwrite the original APK.
set -euo pipefail

APK="${1:-/mnt/data/MotoLauncher3_Ultimate.apk}"
OUT="${2:-./build-work}"
APKTOOL="${APKTOOL:-apktool}"

if [[ ! -f "$APK" ]]; then
  echo "ERROR: APK not found: $APK" >&2
  exit 2
fi

for tool in sha256sum unzip java; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "ERROR: required tool missing: $tool" >&2
    exit 3
  }
done

echo "== Input integrity =="
sha256sum "$APK"
unzip -t "$APK" >/dev/null
echo "ZIP integrity: PASS"

echo
echo "== Required reverse-engineering tools =="
missing=0
for tool in "$APKTOOL" jadx; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '%s: %s\n' "$tool" "$(command -v "$tool")"
  else
    printf '%s: MISSING\n' "$tool"
    missing=1
  fi
done

mkdir -p "$OUT"
cp --reflink=auto -- "$APK" "$OUT/input-original.apk"
sha256sum "$APK" "$OUT/input-original.apk"

if [[ "$missing" -ne 0 ]]; then
  cat >&2 <<'EOF'
STOP: no decompilation or APK changes were attempted.
Install JADX and Apktool using their official distribution channels, then rerun.
Do not patch DEX bytes by guessing offsets and do not install the original mod
over a privileged system package without confirming signing and rollback.
EOF
  exit 4
fi

if [[ -e "$OUT/decoded" ]]; then
  echo "ERROR: $OUT/decoded already exists; refusing to overwrite it." >&2
  exit 5
fi

"$APKTOOL" d -f "$OUT/input-original.apk" -o "$OUT/decoded"
jadx -d "$OUT/java" "$OUT/input-original.apk"

echo
echo "Prepared working copy in: $OUT"
echo "No source changes have been made automatically. Inspect and patch specific code paths next."
