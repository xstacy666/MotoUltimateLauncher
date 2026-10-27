#!/usr/bin/env bash
set -euo pipefail
PATCHED_ROOT="${1:?Usage: restore_stock_recents.sh <patched-root> <decoded-stock-root>}"
DECODED="${2:?Usage: restore_stock_recents.sh <patched-root> <decoded-stock-root>}"

roots=()
while IFS= read -r path; do roots+=("$path"); done < <(find "$DECODED" -maxdepth 1 -type d -name 'smali*' -print | sort)
(("${#roots[@]}" > 0)) || { echo "No stock Smali roots found" >&2; exit 1; }

# Restore complete framework/Quickstep packages that own Recents card geometry,
# paging, overview transitions, and app-launch animations. The custom launcher
# settings classes (including ModStack and Icon Lab) are intentionally untouched.
for pkg in \
  com/android/quickstep \
  com/android/systemui/animation \
  com/android/systemui/shared/system \
  com/android/launcher3/uioverrides; do
  find "$PATCHED_ROOT" -type d -path "*/$pkg" -prune -exec rm -rf {} +
  for stock_root in "${roots[@]}"; do
    if [[ -d "$stock_root/$pkg" ]]; then
      root_name="$(basename "$stock_root")"
      mkdir -p "$PATCHED_ROOT/$root_name/$(dirname "$pkg")"
      cp -a "$stock_root/$pkg" "$PATCHED_ROOT/$root_name/$(dirname "$pkg")/"
    fi
  done
done

# Confirm every restored Recents/transition class byte-for-byte matches the
# original APK decode. Fail the build rather than shipping a mixed implementation.
checked=0
for stock_root in "${roots[@]}"; do
  for pkg in com/android/quickstep com/android/systemui/animation com/android/systemui/shared/system com/android/launcher3/uioverrides; do
    [[ -d "$stock_root/$pkg" ]] || continue
    while IFS= read -r stock_file; do
      rel="${stock_file#"$DECODED/"}"
      patched_file="$PATCHED_ROOT/$rel"
      if [[ ! -f "$patched_file" ]]; then
        echo "::error::Missing restored stock transition class: $rel" >&2
        exit 1
      fi
      if ! cmp -s "$stock_file" "$patched_file"; then
        echo "::error::Recents/transition class differs from original: $rel" >&2
        exit 1
      fi
      ((checked+=1))
    done < <(find "$stock_root/$pkg" -type f -name '*.smali' -print)
  done
done

for rel in \
  smali/com/android/quickstep/views/RecentsView.smali \
  smali/com/android/quickstep/views/TaskView.smali; do
  if [[ -f "$PATCHED_ROOT/$rel" ]]; then continue; fi
  alt="${rel/smali\//smali_classes2/}"
  [[ -f "$PATCHED_ROOT/$alt" ]] || {
    echo "::error::Missing required Recents class: $rel" >&2
    exit 1
  }
done

echo "Verified $checked restored stock Recents/transition Smali files."
