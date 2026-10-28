#!/usr/bin/env python3
"""Prevent a null PreferenceCategory key from crashing LauncherSettingsFragment."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
path = root / "res/xml/launcher_preferences.xml"
if not path.is_file():
    candidates = list((root / "res").rglob("launcher_preferences.xml"))
    if len(candidates) != 1:
        raise SystemExit(f"Could not uniquely locate launcher_preferences.xml under {root}")
    path = candidates[0]

text = path.read_text(encoding="utf-8")
keys = [
    "mod_category_recents",
    "mod_category_dock_studio",
    "mod_category_icon_lab",
    "mod_category_home_screen",
    "mod_category_animations_gestures",
    "mod_category_general",
    "mod_category_search_options",
]
index = 0
changed = 0

def add_key(match):
    global index, changed
    tag = match.group(0)
    if re.search(r"\bandroid:key\s*=", tag):
        return tag
    if index >= len(keys):
        raise SystemExit("Unexpected additional PreferenceCategory without android:key")
    key = keys[index]
    index += 1
    changed += 1
    return tag[:-1] + f' android:key="{key}">'

updated = re.sub(r"<(?:androidx\.preference\.)?PreferenceCategory\b[^>]*>", add_key, text)
if not re.search(r"<(?:androidx\.preference\.)?PreferenceCategory\b", updated):
    raise SystemExit(f"No PreferenceCategory elements found in {path}")
if re.search(r"<(?:androidx\.preference\.)?PreferenceCategory\b(?![^>]*\bandroid:key\s*=)[^>]*>", updated):
    raise SystemExit("At least one PreferenceCategory still has no android:key")
if changed:
    path.write_text(updated, encoding="utf-8")
print(f"Settings null-key fix: assigned keys to {changed} PreferenceCategory element(s) in {path}")
