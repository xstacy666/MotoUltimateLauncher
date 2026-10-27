#!/usr/bin/env python3
"""Fix Recents card spacing/over-rotation and keep Dock Studio drawing through swipe fades."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

def find_smali(rel):
    matches = list(root.glob("smali*/" + rel))
    if len(matches) != 1:
        raise SystemExit(f"Expected one {rel}, found {matches}")
    return matches[0]

# Recents: spread cards horizontally based on their position in the viewport.
# Keep all styles intentionally subtle; the stock style still gets spacing but no 3-D transforms.
stack_path = find_smali("com/android/launcher3/ModStack.smali")
stack = stack_path.read_text()
apply_method = r""".method public static apply(Landroid/view/ViewGroup;)V
    .locals 18

    :try_start_0
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getContext()Landroid/content/Context;
    move-result-object v0
    const-string v1, "mod_recents_style"
    const/4 v2, 0x0
    invoke-static {v0, v1, v2}, Lcom/android/launcher3/ModPrefs;->getInt(Landroid/content/Context;Ljava/lang/String;I)I
    move-result v3

    invoke-virtual {p0}, Landroid/view/ViewGroup;->getWidth()I
    move-result v4
    if-lez v4, :cond_done
    int-to-float v5, v4
    const/high16 v6, 0x3f000000    # 0.5f
    mul-float/2addr v6, v5
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getScrollX()I
    move-result v7
    int-to-float v7, v7
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getChildCount()I
    move-result v8
    const/4 v9, 0x0

    :loop
    if-ge v9, v8, :cond_done
    invoke-virtual {p0, v9}, Landroid/view/ViewGroup;->getChildAt(I)Landroid/view/View;
    move-result-object v10
    instance-of v11, v10, Lcom/android/quickstep/views/TaskView;
    if-eqz v11, :next

    # normalized card center: -1 at far left, +1 at far right
    invoke-virtual {v10}, Landroid/view/View;->getX()F
    move-result v11
    invoke-virtual {v10}, Landroid/view/View;->getWidth()I
    move-result v12
    div-int/lit8 v13, v12, 0x2
    int-to-float v13, v13
    add-float/2addr v11, v13
    sub-float/2addr v11, v7
    sub-float/2addr v11, v6
    div-float/2addr v11, v5
    const/high16 v12, -0x3f800000    # -1.0f
    invoke-static {v11, v12}, Ljava/lang/Math;->max(FF)F
    move-result v11
    const/high16 v12, 0x3f800000    # 1.0f
    invoke-static {v11, v12}, Ljava/lang/Math;->min(FF)F
    move-result v11

    # Push off-center cards outward by 22% of their width at the viewport edge.
    invoke-virtual {v10}, Landroid/view/View;->getWidth()I
    move-result v12
    int-to-float v12, v12
    const v13, 0x3e6147ae    # 0.22f
    mul-float/2addr v12, v13
    mul-float/2addr v12, v11
    invoke-virtual {v10, v12}, Landroid/view/View;->setTranslationX(F)V

    if-nez v3, :style
    const/4 v12, 0x0
    invoke-virtual {v10, v12}, Landroid/view/View;->setRotationY(F)V
    invoke-virtual {v10, v12}, Landroid/view/View;->setRotationX(F)V
    invoke-virtual {v10, v12}, Landroid/view/View;->setRotation(F)V
    invoke-virtual {v10, v12}, Landroid/view/View;->setTranslationZ(F)V
    goto :next

    :style
    invoke-static {v3}, Lcom/android/launcher3/ModStack;->params(I)[F
    move-result-object v15
    const/4 v12, 0x0
    aget v13, v15, v12
    mul-float/2addr v13, v11
    neg-float v13, v13
    invoke-virtual {v10, v13}, Landroid/view/View;->setRotationY(F)V
    const/4 v12, 0x1
    aget v13, v15, v12
    mul-float/2addr v13, v11
    invoke-virtual {v10, v13}, Landroid/view/View;->setRotation(F)V
    invoke-static {v11}, Ljava/lang/Math;->abs(F)F
    move-result v14
    const/4 v12, 0x2
    aget v13, v15, v12
    mul-float/2addr v13, v14
    invoke-virtual {v10, v13}, Landroid/view/View;->setRotationX(F)V
    const/4 v12, 0x3
    aget v13, v15, v12
    mul-float/2addr v13, v14
    neg-float v13, v13
    invoke-virtual {v10, v13}, Landroid/view/View;->setTranslationZ(F)V
    const v12, 0x45fa0000    # 8000.0f
    invoke-virtual {v10, v12}, Landroid/view/View;->setCameraDistance(F)V

    :next
    add-int/lit8 v9, v9, 0x1
    goto :loop

    :cond_done
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0
    return-void
    :catch_0
    move-exception v0
    return-void
.end method"""

stack, count = re.subn(
    r"(?s)\.method public static apply\(Landroid/view/ViewGroup;\)V.*?\.end method",
    apply_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not replace ModStack.apply")

params_method = r""".method public static params(I)[F
    .locals 2
    const/4 v0, 0x4
    new-array v0, v0, [F
    packed-switch p0, :pswitch_data_0
    return-object v0
    :pswitch_0
    fill-array-data v0, :array_0
    return-object v0
    :pswitch_1
    fill-array-data v0, :array_1
    return-object v0
    :pswitch_2
    fill-array-data v0, :array_2
    return-object v0
    :pswitch_3
    fill-array-data v0, :array_3
    return-object v0
    :pswitch_4
    fill-array-data v0, :array_4
    return-object v0
    :pswitch_5
    fill-array-data v0, :array_5
    return-object v0
    :pswitch_6
    fill-array-data v0, :array_6
    return-object v0
    nop
    :pswitch_data_0
    .packed-switch 0x1
        :pswitch_0
        :pswitch_1
        :pswitch_2
        :pswitch_3
        :pswitch_4
        :pswitch_5
        :pswitch_6
    .end packed-switch
    :array_0
    .array-data 4
        0x41000000    # 8.0f
        0x0
        0x0
        0x42a00000    # 80.0f
    .end array-data
    :array_1
    .array-data 4
        0x41400000    # 12.0f
        0x0
        0x0
        0x42700000    # 60.0f
    .end array-data
    :array_2
    .array-data 4
        0x0
        0x40800000    # 4.0f
        0x0
        0x42200000    # 40.0f
    .end array-data
    :array_3
    .array-data 4
        0x41000000    # 8.0f
        0x0
        -0x3f800000    # -1.0f
        0x42700000    # 60.0f
    .end array-data
    :array_4
    .array-data 4
        0x41200000    # 10.0f
        0x40400000    # 3.0f
        0x0
        0x42700000    # 60.0f
    .end array-data
    :array_5
    .array-data 4
        0x41400000    # 12.0f
        0x0
        0x0
        0x42a00000    # 80.0f
    .end array-data
    :array_6
    .array-data 4
        0x41000000    # 8.0f
        -0x40400000    # -3.0f
        0x40400000    # 3.0f
        0x42480000    # 50.0f
    .end array-data
.end method"""
stack, count = re.subn(
    r"(?s)\.method public static params\(I\)\[F.*?\.end method",
    params_method, stack, count=1
)
if count != 1:
    raise SystemExit("Could not replace ModStack.params")
stack_path.write_text(stack)

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

print("Patched Recents spacing/subtle transforms and Dock Studio swipe-fade drawing.")
