#!/usr/bin/env python3
"""Keep stock Quickstep paging intact and implement a safe iOS-style stacked-card transform."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

def find_smali(rel):
    matches = list(root.glob("smali*/" + rel))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {rel}, found {matches}")
    return matches[0]

# Recents: restore stock paging and scrolling behavior. Only clear residual transforms;
# do not calculate card positions or offsets in ModStack.
stack_path = find_smali("com/android/launcher3/ModStack.smali")
stack = stack_path.read_text()
apply_method = r""".method public static apply(Landroid/view/ViewGroup;)V
    .locals 0
    # Quickstep owns TaskView transforms and animations. Never write transforms
    # from this callback: it is invoked during paging/transition frames.
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

# Keep exactly two user-facing Recents choices: Stock and iOS 26 stacked.
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

# First launch should use native Stock Recents rather than opt users into an
# experimental stacked layout before it has been verified on-device.
prefs_path = root / "res/xml/launcher_preferences.xml"
prefs_text = prefs_path.read_text()
style_pref = re.compile(r'(<[^>]+android:key="mod_recents_style"[^>]*android:defaultValue=")1(")')
prefs_text, pref_count = style_pref.subn(r'\g<1>0\2', prefs_text, count=1)
if pref_count != 1:
    # Attribute order can vary; locate the preference element by key first.
    lines = prefs_text.splitlines()
    found = False
    for i, line in enumerate(lines):
        if 'android:key="mod_recents_style"' in line:
            updated, n = re.subn(r'android:defaultValue="[^"]+"', 'android:defaultValue="0"', line, count=1)
            if n != 1:
                raise SystemExit("Could not set Stock Recents default")
            lines[i] = updated
            found = True
            break
    if not found:
        raise SystemExit("Could not find mod_recents_style preference")
    prefs_text = "\n".join(lines) + ("\n" if prefs_text.endswith("\n") else "")
prefs_path.write_text(prefs_text)


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

print("Disabled custom Recents transforms to preserve native Quickstep card layout and animations; applied Dock Studio swipe-fade drawing.")
