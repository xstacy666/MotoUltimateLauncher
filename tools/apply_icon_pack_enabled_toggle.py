#!/usr/bin/env python3
"""Add a safe enable/disable switch for the selected third-party icon pack."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

xml_candidates = list((root / "res").rglob("launcher_preferences.xml"))
if len(xml_candidates) != 1:
    raise SystemExit(f"Expected one launcher_preferences.xml, found {len(xml_candidates)}")
xml_path = xml_candidates[0]
xml = xml_path.read_text(encoding="utf-8")

switch = (
    '<androidx.preference.SwitchPreferenceCompat '
    'android:key="mod_icon_pack_enabled" '
    'android:title="Enable icon pack" '
    'android:summary="Turn the selected third-party icon pack on or off" '
    'android:defaultValue="true" />'
)
if 'android:key="mod_icon_pack_enabled"' not in xml:
    pattern = r'(<com\\.android\\.launcher3\\.widget\\.ModIconPackPreference\\b[^>]*/>)'
    updated, count = re.subn(pattern, r'\\1\n        ' + switch, xml, count=1)
    if count != 1:
        raise SystemExit("Could not locate the existing ModIconPackPreference in launcher_preferences.xml")
    xml_path.write_text(updated, encoding="utf-8")
    print("Added icon-pack enable/disable switch to launcher preferences")
else:
    print("Icon-pack enable/disable switch already exists")

smali_candidates = list(root.glob("smali*/com/android/launcher3/ModIconPack.smali"))
if len(smali_candidates) != 1:
    raise SystemExit(f"Expected one ModIconPack.smali, found {len(smali_candidates)}")
smali_path = smali_candidates[0]
smali = smali_path.read_text(encoding="utf-8")
method_start = smali.find(".method public static get(Landroid/content/Context;Landroid/content/ComponentName;)")
if method_start < 0:
    raise SystemExit("Could not find ModIconPack.get(Context, ComponentName)")
method_end = smali.find(".end method", method_start)
method = smali[method_start:method_end]
needle = '    const-string v0, "mod_icon_pack"'
guard = '''    const-string v0, "mod_icon_pack_enabled"
    invoke-static {p0}, Landroidx/preference/PreferenceManager;->getDefaultSharedPreferences(Landroid/content/Context;)Landroid/content/SharedPreferences;
    move-result-object v1
    const/4 v2, 0x1
    invoke-interface {v1, v0, v2}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v0
    if-nez v0, :mod_icon_pack_enabled
    const/4 v0, 0x0
    return-object v0

    :mod_icon_pack_enabled
'''
if ":mod_icon_pack_enabled" not in method:
    if needle not in method:
        raise SystemExit("Could not find icon-pack selection lookup in ModIconPack.get")
    method = method.replace(needle, guard + needle, 1)
    smali = smali[:method_start] + method + smali[method_end:]
    smali_path.write_text(smali, encoding="utf-8")
    print("Added runtime guard for the icon-pack enabled preference")
else:
    print("Runtime icon-pack enabled guard already exists")
