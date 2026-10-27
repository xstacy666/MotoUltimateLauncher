#!/usr/bin/env python3
"""Keep Quickstep in control of Recents transforms and default to stock layout."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

def find_smali(rel):
    matches = list(root.glob("smali*/" + rel))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {rel}, found {matches}")
    return matches[0]

# Quickstep owns TaskView transforms and animated values.
stack_path = find_smali("com/android/launcher3/ModStack.smali")
stack = stack_path.read_text()
apply_method = r""".method public static apply(Landroid/view/ViewGroup;)V
    .locals 0
    return-void
.end method"""
stack, count = re.subn(
    r"(?s)\.method public static apply\(Landroid/view/ViewGroup;\)V.*?\.end method",
    apply_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not replace ModStack.apply")

params_method = r""".method public static params(I)[F
    .locals 1
    const/4 v0, 0x4
    new-array v0, v0, [F
    return-object v0
.end method"""
stack, count = re.subn(
    r"(?s)\.method public static params\(I\)\[F.*?\.end method",
    params_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not replace ModStack.params")
stack_path.write_text(stack)

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

# Default clean installs to Stock so the custom stack style cannot be the
# source of overlap during first-run testing. Preserve the iOS option.
prefs_path = root / "res/xml/launcher_preferences.xml"
prefs = prefs_path.read_text()
key_match = re.search(r'<[^>]*\bandroid:key="mod_recents_style"[^>]*>', prefs)
if not key_match:
    raise SystemExit("Could not locate mod_recents_style preference in launcher_preferences.xml")
tag = key_match.group(0)
updated_tag, n = re.subn(r'android:defaultValue="[^"]*"', 'android:defaultValue="0"', tag, count=1)
if n == 0:
    if tag.endswith("/>"):
        updated_tag = tag[:-2] + ' android:defaultValue="0" />'
    elif tag.endswith(">"):
        updated_tag = tag[:-1] + ' android:defaultValue="0">'
    else:
        raise SystemExit("Malformed mod_recents_style preference tag")
prefs = prefs[:key_match.start()] + updated_tag + prefs[key_match.end():]
prefs_path.write_text(prefs)

# Keep Dock Studio's glass/background draw path alive during swipe transitions.
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

print("Applied Quickstep-owned Recents transforms, Stock default, and Dock Studio swipe-fade drawing.")
