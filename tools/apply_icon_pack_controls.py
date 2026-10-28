#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1])
xml_files = list((root / "res").rglob("launcher_preferences.xml"))
if len(xml_files) != 1:
    raise SystemExit("Expected one launcher_preferences.xml")
path = xml_files[0]
xml = path.read_text(encoding="utf-8")
if 'android:key="mod_icon_pack_enabled"' not in xml:
    marker = '<com.android.launcher3.widget.ModIconPackPreference'
    start = xml.find(marker)
    if start < 0:
        raise SystemExit("Existing icon pack preference not found")
    end = xml.find("/>", start)
    if end < 0:
        raise SystemExit("Icon pack preference tag is malformed")
    end += 2
    switch = '\n        <androidx.preference.SwitchPreferenceCompat android:key="mod_icon_pack_enabled" android:title="Enable icon pack" android:summary="Turn the selected third-party icon pack on or off" android:defaultValue="true" />'
    xml = xml[:end] + switch + xml[end:]
    path.write_text(xml, encoding="utf-8")
    print("Added icon pack enable switch")

files = list(root.glob("smali*/com/android/launcher3/ModIconPack.smali"))
if len(files) != 1:
    raise SystemExit("Expected one ModIconPack.smali")
path = files[0]
smali = path.read_text(encoding="utf-8")
start = smali.find(".method public static get(Landroid/content/Context;Landroid/content/ComponentName;)")
end = smali.find(".end method", start)
if start < 0 or end < 0:
    raise SystemExit("ModIconPack.get method not found")
method = smali[start:end]
if ":mod_icon_pack_enabled" not in method:
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
    if needle not in method:
        raise SystemExit("Icon pack lookup insertion point not found")
    method = method.replace(needle, guard + needle, 1)
    path.write_text(smali[:start] + method + smali[end:], encoding="utf-8")
    print("Added runtime icon pack enable check")
