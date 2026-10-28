#!/usr/bin/env python3
"""Add enable/disable and explicit reset-to-default behavior for icon packs."""
from pathlib import Path
import sys

root = Path(sys.argv[1])

xml_files = list((root / "res").rglob("launcher_preferences.xml"))
if len(xml_files) != 1:
    raise SystemExit("Expected one launcher_preferences.xml")
xml_path = xml_files[0]
xml = xml_path.read_text(encoding="utf-8")

# Move the picker and enable switch into a clearly visible top-level category.
import re
picker_matches = list(re.finditer(
    r'<com\.android\.launcher3\.widget\.ModIconPackPreference\b[^>]*/>', xml, re.S
))
if len(picker_matches) != 1:
    raise SystemExit(f"Expected one icon-pack picker XML node, found {len(picker_matches)}")
picker = picker_matches[0].group(0)
xml = xml[:picker_matches[0].start()] + xml[picker_matches[0].end():]

switch_matches = list(re.finditer(
    r'<androidx\.preference\.SwitchPreferenceCompat\b(?=[^>]*android:key="mod_icon_pack_enabled")[^>]*/>', xml, re.S
))
if len(switch_matches) > 1:
    raise SystemExit("Found duplicate icon-pack enable switches")
if switch_matches:
    switch = switch_matches[0].group(0)
    xml = xml[:switch_matches[0].start()] + xml[switch_matches[0].end():]
else:
    switch = '<androidx.preference.SwitchPreferenceCompat android:key="mod_icon_pack_enabled" android:title="Enable icon pack" android:summary="Turn the selected third-party icon pack on or off" android:defaultValue="true" />'

root_match = re.search(r'<(?:androidx\.preference\.)?PreferenceScreen\b[^>]*>', xml)
if not root_match:
    raise SystemExit("Could not find root PreferenceScreen in launcher_preferences.xml")
category = (
    '\n    <PreferenceCategory android:key="icon_pack_controls" android:title="Icon pack controls">'
    + '\n        ' + picker
    + '\n        ' + switch
    + '\n    </PreferenceCategory>\n'
)
xml = xml[:root_match.end()] + category + xml[root_match.end():]
xml_path.write_text(xml, encoding="utf-8")
print("Placed icon-pack picker and enable switch in a visible top-level category")

pack_files = list(root.glob("smali*/com/android/launcher3/ModIconPack.smali"))
if len(pack_files) != 1:
    raise SystemExit("Expected one ModIconPack.smali")
pack_path = pack_files[0]
pack = pack_path.read_text(encoding="utf-8")
start = pack.find(".method public static get(Landroid/content/Context;Landroid/content/ComponentName;)")
end = pack.find(".end method", start)
if start < 0 or end < 0:
    raise SystemExit("ModIconPack.get method not found")
method = pack[start:end]
if ":mod_icon_pack_enabled" not in method:
    needle = '    const-string v0, "mod_icon_pack"'
    guard = '''    const-string v0, "com.android.launcher3.prefs"
    const/4 v1, 0x0
    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v1
    const-string v0, "mod_icon_pack_enabled"
    const/4 v2, 0x1
    invoke-interface {v1, v0, v2}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v0
    if-nez v0, :mod_icon_pack_enabled
    const/4 v0, 0x0
    return-object v0

    :mod_icon_pack_enabled
'''
    if needle not in method:
        raise SystemExit("Icon pack lookup insertion point not found")
    method = method.replace(needle, guard + needle, 1)
    pack_path.write_text(pack[:start] + method + pack[end:], encoding="utf-8")
    print("Added runtime icon pack enable check")

widget_files = list(root.glob("smali*/com/android/launcher3/widget/ModIconPackPreference.smali"))
if len(widget_files) != 1:
    raise SystemExit("Expected one ModIconPackPreference.smali")
widget_path = widget_files[0]
widget = widget_path.read_text(encoding="utf-8")
widget = widget.replace('const-string v2, "System default"', 'const-string v2, "Remove pack (System default)"', 1)
widget_path.write_text(widget, encoding="utf-8")

prefs_files = list(root.glob("smali*/com/android/launcher3/ModPrefs.smali"))
if len(prefs_files) != 1:
    raise SystemExit("Expected one ModPrefs.smali")
prefs_path = prefs_files[0]
prefs = prefs_path.read_text(encoding="utf-8")
old = '''    if-eqz v0, :cond_1

    :cond_0
'''
new = '''    if-eqz v0, :check_icon_pack_enabled
    goto :cond_0

    :check_icon_pack_enabled
    const-string v0, "mod_icon_pack_enabled"
    invoke-virtual {v0, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    move-result v0

    if-eqz v0, :cond_1

    :cond_0
'''
if ":check_icon_pack_enabled" not in prefs:
    if old not in prefs:
        raise SystemExit("Could not locate ModPrefs.onChanged restart condition")
    prefs = prefs.replace(old, new, 1)
    prefs_path.write_text(prefs, encoding="utf-8")
    print("Enabled icon cache refresh and launcher restart when toggled")
print("Icon pack enable and reset controls patched")
