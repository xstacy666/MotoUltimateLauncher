#!/usr/bin/env bash
# Repeatable static analysis for Moto Ultimate Launcher APKs.
# Does not patch, sign, install, or modify the input APK.
set -euo pipefail

usage() { echo 'Usage: tools/analyze_launcher_apk.sh <launcher.apk> [output-directory]' >&2; }
APK="${1:-}"
OUT="${2:-}"
if [[ -z "$APK" || ! -f "$APK" ]]; then usage; echo 'ERROR: APK file not found.' >&2; exit 2; fi
APK="$(cd "$(dirname "$APK")" && pwd)/$(basename "$APK")"
if [[ -z "$OUT" ]]; then OUT="./analysis/launcher-$(date -u +%Y%m%dT%H%M%SZ)"; fi
for tool in java unzip sha256sum apktool jadx; do
  command -v "$tool" >/dev/null 2>&1 || { echo "ERROR: missing required tool: $tool" >&2; exit 3; }
done
if [[ -e "$OUT" ]]; then echo "ERROR: output already exists; refusing to overwrite: $OUT" >&2; exit 4; fi
mkdir -p "$(dirname "$OUT")"
mkdir "$OUT"
REPORT="$OUT/REPORT.md"
{
  echo '# Moto Ultimate Launcher — static analysis report'; echo
  echo "- Input APK: $APK"
  echo "- Generated UTC: $(date -u +%FT%TZ)"
  echo '- SHA-256:'; echo '  ```'; sha256sum "$APK"; echo '  ```'
} > "$REPORT"
unzip -t "$APK" > "$OUT/zip-integrity.txt"
echo 'PASS: APK ZIP integrity' | tee -a "$OUT/zip-integrity.txt"
apktool d --force "$APK" -o "$OUT/resources"
if ! jadx --show-bad-code -d "$OUT/java" "$APK" > "$OUT/jadx.log" 2>&1; then
  echo "WARNING: JADX returned non-zero; inspect $OUT/jadx.log. Partial output retained." | tee -a "$REPORT"
fi
{
  echo; echo '## Tool versions'; echo
  echo "- Java: $(java -version 2>&1 | head -n 1)"
  echo "- Apktool: $(apktool --version 2>&1 | head -n 1)"
  echo "- JADX: $(jadx --version 2>&1 | head -n 1)"
  echo; echo '## Relevant source hits'; echo
  echo 'Search hits are leads for manual review, not proof that a feature works.'; echo
  echo '```text'
  grep -RInE --include='*.java' --include='*.kt' --include='*.xml' --include='*.smali' 'TaskView|RecentsView|TaskStack|Overview|IconPack|icon.pack|ModPrefs|translationZ|rotationX|setTranslation|setScale' "$OUT/java" "$OUT/resources" 2>/dev/null | head -n 250 || true
  echo '```'; echo; echo '## Outputs'; echo
  echo '- resources/: Apktool-decoded resources, manifest, and smali'
  echo '- java/: JADX-decompiled source'; echo '- zip-integrity.txt: APK container integrity result'; echo '- jadx.log: decompiler diagnostics'
  echo; echo '## Limits'; echo
  echo '- Decompiled Java is an approximation of bytecode; verify behavior against smali and original source where available.'
  echo '- Static analysis cannot confirm animation timing or card spacing on a real device.'
  echo '- This script never modifies or signs the input APK.'
} >> "$REPORT"
echo "Analysis complete: $OUT"
echo "Report: $REPORT"
