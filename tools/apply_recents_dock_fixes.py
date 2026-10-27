#!/usr/bin/env python3
"""Preserve native Quickstep transforms while restoring Recents spacing and Icon Lab build patches."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

def find_smali(rel):
    matches = list(root.glob("smali*/" + rel))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {rel}, found {matches}")
    return matches[0]

# Quickstep must own TaskView transforms: custom per-frame transforms conflict with
# Recents transition animations. Keep this callback inert, but preserve the native
# parameter preset values below because Quickstep uses them for card spacing.
stack_path = find_smali("com/android/launcher3/ModStack.smali")
stack = stack_path.read_text()
apply_method = """.method public static apply(Landroid/view/ViewGroup;)V
    .locals 0
    # Do not overwrite TaskView transforms during Quickstep paging/transition frames.
    return-void
.end method"""
stack, count = re.subn(
    r"(?s)\.method public static apply\(Landroid/view/ViewGroup;\)V.*?\.end method",
    apply_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not replace ModStack.apply")

# Stock (0) keeps the native zero-offset preset; iOS (1) retains its 24dp
# spacing preset so cards do not collapse onto one another.
params_method = """.method public static params(I)[F
    .locals 1
    const/4 v0, 0x4
    new-array v0, v0, [F
    if-eqz p0, :params_done
    fill-array-data v0, :ios_array
    :params_done
    return-object v0
    :ios_array
    .array-data 4
        0x0
        0x0
        0x0
        0x41c00000
    .end array-data
.end method"""
stack, count = re.subn(
    r"(?s)\.method public static params\(I\)\[F.*?\.end method",
    params_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not restore ModStack.params spacing preset")
stack_path.write_text(stack)

# Keep exactly two user-facing Recents choices.
arrays_path = root / "res/values/arrays.xml"
arrays_text = arrays_path.read_text()
def replace_string_array(source, name, items):
    pattern = re.compile(r'(?s)(<string-array name="' + re.escape(name) + r'">).*?(</string-array>)')
    body = "\n".join("        <item>" + item + "</item>" for item in items)
    updated, n = pattern.subn(lambda m: m.group(1) + "\n" + body + "\n    " + m.group(2), source, count=1)
    if n != 1:
        raise SystemExit("Could not find " + name + " in arrays.xml")
    return updated
arrays_text = replace_string_array(arrays_text, "mod_recents_entries", ["Stock", "iOS 26 stacked"])
arrays_text = replace_string_array(arrays_text, "mod_recents_values", ["0", "1"])
arrays_path.write_text(arrays_text)

# Default to Stock for first launch; users can still select iOS 26 stacked.
prefs_path = root / "res/xml/launcher_preferences.xml"
prefs = prefs_path.read_text()
key_pos = prefs.find('key="mod_recents_style"')
if key_pos < 0:
    key_pos = prefs.find('android:key="mod_recents_style"')
if key_pos < 0:
    raise SystemExit("Could not find mod_recents_style preference")
tag_start = prefs.rfind("<", 0, key_pos)
tag_end = prefs.find(">", key_pos)
if tag_start < 0 or tag_end < 0:
    raise SystemExit("Could not locate Recents preference XML tag")
tag = prefs[tag_start:tag_end + 1]
if 'defaultValue="0"' not in tag and 'android:defaultValue="0"' not in tag:
    tag_new, n = re.subn(r'((?:android:)?defaultValue=")[^"]*(")', r'\g<1>0\2', tag, count=1)
    if n == 0:
        # Insert a default only if this preference doesn't declare one.
        tag_new = tag[:-1] + ' android:defaultValue="0">'
    prefs = prefs[:tag_start] + tag_new + prefs[tag_end + 1:]
    prefs_path.write_text(prefs)

# Dock: don't skip drawing the glass/background merely because Hotseat's alpha
# briefly drops during swipe transitions. The parent still composites the view alpha.
dock_path = find_smali("com/android/launcher3/DockBlur.smali")
dock = dock_path.read_text()
alpha_gate = re.compile(
    r"(?m)^    invoke-virtual \{p0\}, Landroid/view/View;->getAlpha\(\)F\s*\n"
    r"\s*move-result v1\s*\n"
    r"\s*const v2, 0x3c23d70a[^\n]*\n"
    r"\s*cmpg-float v2, v1, v2\s*\n"
    r"\s*if-ltz v2, :cond_7\s*\n"
)
dock, count = alpha_gate.subn(
    "    invoke-virtual {p0}, Landroid/view/View;->getAlpha()F\n\n    move-result v1\n",
    dock, count=1
)
if count != 1:
    raise SystemExit("Could not locate DockBlur alpha early-return gate")
dock_path.write_text(dock)

print("Preserved Quickstep animation ownership, restored Recents spacing presets, defaulted Recents to Stock, and applied Dock Studio swipe-fade drawing.")
