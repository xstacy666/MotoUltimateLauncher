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
    .locals 15
    :try_start_0
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getContext()Landroid/content/Context;
    move-result-object v0
    const-string v1, "mod_recents_style"
    const/4 v2, 0x0
    invoke-static {v0, v1, v2}, Lcom/android/launcher3/ModPrefs;->getInt(Landroid/content/Context;Ljava/lang/String;I)I
    move-result v8
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getWidth()I
    move-result v0
    if-lez v0, :done
    int-to-float v1, v0
    const/high16 v2, 0x40000000
    div-float/2addr v1, v2
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getScrollX()I
    move-result v3
    int-to-float v3, v3
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getChildCount()I
    move-result v4
    const/4 v5, 0x0
    :loop
    if-ge v5, v4, :done
    invoke-virtual {p0, v5}, Landroid/view/ViewGroup;->getChildAt(I)Landroid/view/View;
    move-result-object v6
    instance-of v7, v6, Lcom/android/quickstep/views/TaskView;
    if-eqz v7, :next
    if-nez v8, :stacked
    const/4 v9, 0x0
    invoke-virtual {v6, v9}, Landroid/view/View;->setRotationY(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setRotationX(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setRotation(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setTranslationZ(F)V
    const/high16 v9, 0x3f800000
    invoke-virtual {v6, v9}, Landroid/view/View;->setScaleX(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setScaleY(F)V
    goto :next
    :stacked
    invoke-virtual {v6}, Landroid/view/View;->getX()F
    move-result v7
    invoke-virtual {v6}, Landroid/view/View;->getWidth()I
    move-result v9
    div-int/lit8 v9, v9, 0x2
    int-to-float v9, v9
    add-float/2addr v7, v9
    sub-float/2addr v7, v3
    sub-float/2addr v7, v1
    invoke-static {v7}, Ljava/lang/Math;->abs(F)F
    move-result v9
    div-float/2addr v9, v1
    const/high16 v10, 0x3f800000
    invoke-static {v9, v10}, Ljava/lang/Math;->min(FF)F
    move-result v9
    const v10, 0x3dcccccd
    mul-float/2addr v10, v9
    const/high16 v11, 0x3f800000
    sub-float/2addr v11, v10
    invoke-virtual {v6, v11}, Landroid/view/View;->setScaleX(F)V
    invoke-virtual {v6, v11}, Landroid/view/View;->setScaleY(F)V
    const/high16 v10, 0x3f800000
    sub-float/2addr v10, v9
    const/high16 v12, 0x41c00000
    mul-float/2addr v10, v12
    invoke-virtual {v6, v10}, Landroid/view/View;->setTranslationZ(F)V
    const/4 v10, 0x0
    invoke-virtual {v6, v10}, Landroid/view/View;->setRotationY(F)V
    invoke-virtual {v6, v10}, Landroid/view/View;->setRotationX(F)V
    invoke-virtual {v6, v10}, Landroid/view/View;->setRotation(F)V
    :next
    add-int/lit8 v5, v5, 0x1
    goto :loop
    :done
    return-void
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0
    :catch_0
    move-exception v0
    return-void
.end method"""

stack, count = re.subn(stack, count = re.subn(
    r"(?s)\.method public static apply\(Landroid/view/ViewGroup;\)V.*?\.end method",
    apply_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not replace ModStack.apply")

params_method = r""".method public static params(I)[F
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
stack, count = re.subn(stack, count = re.subn(
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

print("Applied two-mode Recents (Stock/iOS 26 stacked), safe card scaling, and Dock Studio swipe-fade drawing.")
