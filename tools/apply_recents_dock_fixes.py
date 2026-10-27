#!/usr/bin/env python3
"""Safe iOS-style stacked Recents + Dock fix. Conservative Smali that should assemble."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

def find_smali(rel):
    matches = list(root.glob("smali*/" + rel))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {rel}, found {matches}")
    return matches[0]

stack_path = find_smali("com/android/launcher3/ModStack.smali")
stack = stack_path.read_text()

# Conservative apply method — fewer registers, simple control flow
apply_method = r""".method public static apply(Landroid/view/ViewGroup;)V
    .locals 12

    :try_start_0
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getContext()Landroid/content/Context;
    move-result-object v0

    const-string v1, "mod_recents_style"
    const/4 v2, 0x0
    invoke-static {v0, v1, v2}, Lcom/android/launcher3/ModPrefs;->getInt(Landroid/content/Context;Ljava/lang/String;I)I
    move-result v0

    invoke-virtual {p0}, Landroid/view/ViewGroup;->getWidth()I
    move-result v1
    if-gtz v1, :done

    int-to-float v1, v1
    const/high16 v2, 0x40000000    # 2.0f
    div-float v1, v1, v2

    invoke-virtual {p0}, Landroid/view/ViewGroup;->getScrollX()I
    move-result v2
    int-to-float v2, v2

    invoke-virtual {p0}, Landroid/view/ViewGroup;->getChildCount()I
    move-result v3

    const/4 v4, 0x0

    :loop
    if-ge v4, v3, :done

    invoke-virtual {p0, v4}, Landroid/view/ViewGroup;->getChildAt(I)Landroid/view/View;
    move-result-object v5

    instance-of v6, v5, Lcom/android/quickstep/views/TaskView;
    if-eqz v6, :next

    if-nez v0, :do_stacked

    const/4 v6, 0x0
    invoke-virtual {v5, v6}, Landroid/view/View;->setRotationY(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setRotationX(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setRotation(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setTranslationX(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setTranslationZ(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setTranslationY(F)V
    const/high16 v6, 0x3f800000    # 1.0f
    invoke-virtual {v5, v6}, Landroid/view/View;->setScaleX(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setScaleY(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setAlpha(F)V
    goto :next

    :do_stacked
    invoke-virtual {v5}, Landroid/view/View;->getX()F
    move-result v6
    invoke-virtual {v5}, Landroid/view/View;->getWidth()I
    move-result v7
    div-int/lit8 v7, v7, 0x2
    int-to-float v7, v7
    add-float/2addr v6, v7
    sub-float/2addr v6, v2
    sub-float/2addr v6, v1
    invoke-static {v6}, Ljava/lang/Math;->abs(F)F
    move-result v6
    div-float/2addr v6, v1
    const/high16 v7, 0x3f800000    # 1.0f
    invoke-static {v6, v7}, Ljava/lang/Math;->min(FF)F
    move-result v6

    const v7, 0x3eb33333    # 0.35f
    mul-float v7, v7, v6
    const/high16 v8, 0x3f800000    # 1.0f
    sub-float v7, v8, v7
    invoke-virtual {v5, v7}, Landroid/view/View;->setScaleX(F)V
    invoke-virtual {v5, v7}, Landroid/view/View;->setScaleY(F)V

    const/high16 v7, 0x42c80000    # 100.0f
    mul-float v7, v7, v6
    invoke-virtual {v5, v7}, Landroid/view/View;->setTranslationY(F)V

    sub-float v7, v8, v6
    const/high16 v9, 0x428c0000    # 70.0f
    mul-float v7, v7, v9
    invoke-virtual {v5, v7}, Landroid/view/View;->setTranslationZ(F)V

    const v7, 0x3f000000    # 0.5f
    mul-float v7, v7, v6
    sub-float v7, v8, v7
    invoke-virtual {v5, v7}, Landroid/view/View;->setAlpha(F)V

    const/4 v6, 0x0
    invoke-virtual {v5, v6}, Landroid/view/View;->setRotationY(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setRotationX(F)V
    invoke-virtual {v5, v6}, Landroid/view/View;->setRotation(F)V

    :next
    add-int/lit8 v4, v4, 0x1
    goto :loop

    :done
    return-void

    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    :catch_0
    move-exception v0
    return-void
.end method"""

stack, count = re.subn(
    r"(?s)\.method public static apply\(Landroid/view/ViewGroup;\)V.*?\.end method",
    apply_method,
    stack,
    count=1,
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
        0x42200000
    .end array-data
.end method"""

stack, count = re.subn(
    r"(?s)\.method public static params\(I\)\[F.*?\.end method",
    params_method,
    stack,
    count=1,
)
if count != 1:
    raise SystemExit("Could not replace ModStack.params")

stack_path.write_text(stack)

# Preference labels
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

# Dock alpha fix
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
    dock,
    count=1,
)
if count != 1:
    raise SystemExit("Could not locate DockBlur alpha early-return gate")
dock_path.write_text(dock)

print("Applied safe iOS 26 stacked Recents + Dock fix.")
