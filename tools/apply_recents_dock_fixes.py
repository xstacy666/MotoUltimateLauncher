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
    .locals 13

    :try_start_0
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getWidth()I
    move-result v0
    if-lez v0, :cond_done
    int-to-float v1, v0
    const/high16 v2, 0x3f000000    # 0.5f
    mul-float/2addr v2, v1
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getChildCount()I
    move-result v4
    const/4 v5, 0x0

    :loop
    if-ge v5, v4, :cond_done
    invoke-virtual {p0, v5}, Landroid/view/ViewGroup;->getChildAt(I)Landroid/view/View;
    move-result-object v6
    instance-of v7, v6, Lcom/android/quickstep/views/TaskView;
    if-eqz v7, :next

    # Re-read scroll each pass because scratch registers are reused below.
    invoke-virtual {p0}, Landroid/view/ViewGroup;->getScrollX()I
    move-result v3
    int-to-float v3, v3

    # normalized card center: -1 at far left, +1 at far right
    invoke-virtual {v6}, Landroid/view/View;->getX()F
    move-result v8
    invoke-virtual {v6}, Landroid/view/View;->getWidth()I
    move-result v9
    div-int/lit8 v12, v9, 0x2
    int-to-float v12, v12
    add-float/2addr v8, v12
    sub-float/2addr v8, v3
    sub-float/2addr v8, v2
    div-float/2addr v8, v1
    const/high16 v9, -0x3f800000    # -1.0f
    invoke-static {v8, v9}, Ljava/lang/Math;->max(FF)F
    move-result v8
    const/high16 v9, 0x3f800000    # 1.0f
    invoke-static {v8, v9}, Ljava/lang/Math;->min(FF)F
    move-result v8

    # Spread off-center cards outward by 22% of their width at the viewport edge.
    invoke-virtual {v6}, Landroid/view/View;->getWidth()I
    move-result v9
    int-to-float v9, v9
    const v10, 0x3e6147ae    # 0.22f
    mul-float/2addr v9, v10
    mul-float/2addr v9, v8
    invoke-virtual {v6, v9}, Landroid/view/View;->setTranslationX(F)V

    # Avoid the excessive 3-D transforms that made cards overlap/distort.
    const/4 v9, 0x0
    invoke-virtual {v6, v9}, Landroid/view/View;->setRotationY(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setRotationX(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setRotation(F)V
    invoke-virtual {v6, v9}, Landroid/view/View;->setTranslationZ(F)V

    :next
    add-int/lit8 v5, v5, 0x1
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
