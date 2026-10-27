#!/usr/bin/env bash
set -euo pipefail

BASELINE="${1:?Usage: verify_compiled_changes.sh <original.apk> <rebuilt.apk>}"
BUILT="${2:?Usage: verify_compiled_changes.sh <original.apk> <rebuilt.apk>}"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/base" "$TMP/built"

test -s "$BASELINE"
test -s "$BUILT"
unzip -tq "$BASELINE"
unzip -tq "$BUILT"

unzip -q "$BASELINE" 'classes*.dex' -d "$TMP/base"
unzip -q "$BUILT" 'classes*.dex' -d "$TMP/built"
mapfile -t base_dex < <(find "$TMP/base" -type f -name 'classes*.dex' -printf '%f\n' | sort)
mapfile -t built_dex < <(find "$TMP/built" -type f -name 'classes*.dex' -printf '%f\n' | sort)
test "${#base_dex[@]}" -gt 0 || { echo "Baseline has no DEX files" >&2; exit 1; }
test "${#built_dex[@]}" -gt 0 || { echo "Rebuilt APK has no DEX files" >&2; exit 1; }

changed=0
for dex in "${built_dex[@]}"; do
  if [[ ! -f "$TMP/base/$dex" ]]; then
    echo "New compiled DEX: $dex"
    changed=1
  elif ! cmp -s "$TMP/base/$dex" "$TMP/built/$dex"; then
    echo "Compiled DEX differs from original: $dex"
    changed=1
  else
    echo "Unchanged compiled DEX: $dex"
  fi
done
for dex in "${base_dex[@]}"; do
  if [[ ! -f "$TMP/built/$dex" ]]; then
    echo "Original DEX removed by build: $dex" >&2
    exit 1
  fi
done
if [[ "$changed" -ne 1 ]]; then
  echo "::error::Rebuilt APK has no compiled DEX changes versus the original. Refusing to publish an unchanged APK." >&2
  exit 1
fi

# Confirm the code path intended to control Recents actually made it into DEX.
find "$TMP/built" -type f -name 'classes*.dex' -print0 | xargs -0 strings > "$TMP/dex-strings.txt"
if ! grep -q 'ModStack' "$TMP/dex-strings.txt"; then
  echo "::error::Compiled DEX does not contain ModStack; Recents patch is not present." >&2
  exit 1
fi
if ! grep -q 'mod_recents_style' "$TMP/dex-strings.txt"; then
  echo "::error::Compiled DEX does not contain mod_recents_style; Recents preference is not wired into code." >&2
  exit 1
fi

# Check the actual compiled resource table for the two allowed user-facing modes.
unzip -p "$BUILT" resources.arsc | strings > "$TMP/resources.txt"
grep -Fq 'Stock' "$TMP/resources.txt" || { echo "::error::Recents 'Stock' label missing from compiled resources." >&2; exit 1; }
grep -Fq 'iOS 26 stacked' "$TMP/resources.txt" || { echo "::error::Recents 'iOS 26 stacked' label missing from compiled resources." >&2; exit 1; }

echo "PASS: rebuilt APK has changed compiled DEX, contains the Recents code path, and packages Stock + iOS 26 stacked resource labels."
