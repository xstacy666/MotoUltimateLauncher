#!/usr/bin/env bash
# Static analysis for either an APK or an already-decoded Apktool project.
# Never modifies, signs, or installs the supplied input.
set -euo pipefail
usage() { echo 'Usage: tools/analyze_launcher_apk.sh <launcher.apk|decoded-project-dir> [output-directory]' >&2; }
INPUT="${1:-}"
OUT="${2:-}"
if [[ -z "$INPUT" || ( ! -f "$INPUT" && ! -d "$INPUT" ) ]]; then usage; echo 'ERROR: input APK/project not found.' >&2; exit 2; fi
INPUT="$(cd "$(dirname "$INPUT")" 2>/dev/null && pwd)/$(basename "$INPUT")" 2>/dev/null || INPUT="$(cd "$INPUT" && pwd)"
if [[ -z "$OUT" ]]; then OUT="./analysis/launcher-$(date -u +%Y%m%dT%H%M%SZ)"; fi
if [[ -e "$OUT" ]]; then echo "ERROR: output already exists; refusing to overwrite: $OUT" >&2; exit 4; fi
mkdir -p "$(dirname "$OUT")"; mkdir "$OUT"
REPORT="$OUT/REPORT.md"
{
 echo '# Moto Ultimate Launcher — static analysis report'; echo
 echo "- Input: $INPUT"; echo "- Generated UTC: $(date -u +%FT%TZ)"
 if [[ -f "$INPUT" ]]; then echo '- SHA-256:'; echo '  ```'; sha256sum "$INPUT"; echo '  ```'; fi
} > "$REPORT"
if [[ -f "$INPUT" ]]; then
 for tool in java unzip sha256sum apktool jadx; do command -v "$tool" >/dev/null 2>&1 || { echo "ERROR: missing required tool: $tool" >&2; exit 3; }; done
 unzip -t "$INPUT" > "$OUT/zip-integrity.txt"
 echo 'PASS: APK ZIP integrity' | tee -a "$OUT/zip-integrity.txt"
 apktool d --force "$INPUT" -o "$OUT/resources"
 if ! jadx --show-bad-code -d "$OUT/java" "$INPUT" > "$OUT/jadx.log" 2>&1; then echo "WARNING: JADX returned non-zero; inspect $OUT/jadx.log. Partial output retained." | tee -a "$REPORT"; fi
 SEARCH_ROOTS="$OUT/java $OUT/resources"
 echo '- Input type: APK; decoded with Apktool and JADX.' >> "$REPORT"
else
 [[ -f "$INPUT/apktool.yml" ]] || { echo 'ERROR: directory must be an Apktool-decoded project containing apktool.yml.' >&2; exit 2; }
 command -v sha256sum >/dev/null 2>&1 || { echo 'ERROR: sha256sum is required.' >&2; exit 3; }
 cp -a "$INPUT" "$OUT/project"
 SEARCH_ROOTS="$OUT/project"
 echo '- Input type: decoded Apktool project; no resource relinking attempted.' >> "$REPORT"
fi
{
 echo; echo '## Tool versions'; echo
 command -v java >/dev/null 2>&1 && echo "- Java: $(java -version 2>&1 | head -n 1)" || true
 command -v apktool >/dev/null 2>&1 && echo "- Apktool: $(apktool --version 2>&1 | head -n 1)" || true
 command -v jadx >/dev/null 2>&1 && echo "- JADX: $(jadx --version 2>&1 | head -n 1)" || true
 echo; echo '## Relevant source hits'; echo
 echo 'Search hits are leads for manual review, not proof that a feature works.'; echo
 echo '```text'
 # shellcheck disable=SC2086
 grep -RInE --include='*.java' --include='*.kt' --include='*.xml' --include='*.smali' 'TaskView|RecentsView|TaskStack|Overview|IconPack|icon.pack|ModPrefs|translationZ|rotationX|setTranslation|setScale|mod_icon_pack' $SEARCH_ROOTS 2>/dev/null | head -n 400 || true
 echo '```'; echo; echo '## Outputs'; echo
 [[ -d "$OUT/project" ]] && echo '- project/: copied decoded project' || true
 [[ -d "$OUT/java" ]] && echo '- java/: JADX-decompiled source' || true
 [[ -d "$OUT/resources" ]] && echo '- resources/: Apktool-decoded resources and smali' || true
 [[ -f "$OUT/zip-integrity.txt" ]] && echo '- zip-integrity.txt: APK container integrity result' || true
 [[ -f "$OUT/jadx.log" ]] && echo '- jadx.log: decompiler diagnostics' || true
 echo; echo '## Limits'; echo
 echo '- Decompiled Java is approximate; verify against smali and source where available.'
 echo '- Static analysis cannot confirm animation timing or spacing on a real device.'
 echo '- This script never modifies, signs, or installs the input.'
} >> "$REPORT"
echo "Analysis complete: $OUT"; echo "Report: $REPORT"
