#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])

# OEM settings contain preferences without a key. initPreference() hashes the
# key before checking it, causing an immediate NPE on Android 16 / this build.
settings_candidates = list(root.glob("smali*/com/android/launcher3/settings/SettingsActivity$LauncherSettingsFragment.smali"))
if len(settings_candidates) != 1:
    raise SystemExit(f"Expected exactly one settings fragment Smali file, found: {settings_candidates}")
settings = settings_candidates[0]
settings_text = settings.read_text()
signature = re.search(
    r"(?m)^\.method[^\n]*\binitPreference\(Landroidx/preference/Preference;\)([VZ])[^\n]*$",
    settings_text,
)
if not signature:
    raise SystemExit("Could not locate initPreference(Preference) method signature")
method_start = signature.start()
method_end = settings_text.find(".end method", signature.end())
if method_end < 0:
    raise SystemExit("Could not find end of initPreference method")
method = settings_text[method_start:method_end]
if ":mod_null_preference_key" not in method:
    # Null keys are legal for preference categories. Guard hashCode dispatches
    # before the switch without depending on exact compiler formatting.
    pattern = re.compile(
        r"(?m)^([ \t]*)invoke-virtual \{([vp]\d+)\}, .*->hashCode\(\)I"
    )
    matches = list(pattern.finditer(method))
    if not matches:
        # Some builds use a virtual call with a different owner descriptor.
        pattern = re.compile(
            r"(?m)^([ \t]*)invoke-virtual \{([vp]\d+)\}, [^\n]*hashCode\(\)I"
        )
        matches = list(pattern.finditer(method))
    if not matches:
        raise SystemExit("Could not find hashCode() dispatch in initPreference")
    for match in reversed(matches):
        indent, reg = match.group(1), match.group(2)
        guard = indent + f"if-eqz {reg}, :mod_null_preference_key\n"
        method = method[:match.start()] + guard + method[match.start():]
    return_type = signature.group(1)
    if return_type == "V":
        epilogue = "\n    :mod_null_preference_key\n    return-void\n"
    else:
        epilogue = "\n    :mod_null_preference_key\n    const/4 v0, 0x1\n    return v0\n"
    method += epilogue
    settings_text = settings_text[:method_start] + method + settings_text[method_end:]
    settings.write_text(settings_text)
    print(f"Added null-safe hashCode guards ({len(matches)} call(s)) to initPreference.")
else:
    print("Null-key guard already present.")

draw_method = r""".method public static draw(Landroid/graphics/drawable/Drawable;Landroid/graphics/Canvas;Landroid/content/Context;)V
    .locals 14

    :try_start_0
    move-object/from16 v13, p2

    const-string v0, "mod_icon_shape"

    const/4 v1, 0x0

    invoke-static {v13, v0, v1}, Lcom/android/launcher3/ModPrefs;->getInt(Landroid/content/Context;Ljava/lang/String;I)I

    move-result v0

    const-string v1, "mod_icon_zoom"

    const/16 v2, 0x64

    invoke-static {v13, v1, v2}, Lcom/android/launcher3/ModPrefs;->getInt(Landroid/content/Context;Ljava/lang/String;I)I

    move-result v1

    const-string v2, "mod_icon_inset"

    const/4 v3, 0x0

    invoke-static {v13, v2, v3}, Lcom/android/launcher3/ModPrefs;->getInt(Landroid/content/Context;Ljava/lang/String;I)I

    move-result v2

    instance-of v3, p0, Landroid/graphics/drawable/AdaptiveIconDrawable;

    if-eqz v3, :draw_original

    if-eqz v0, :check_default_settings

    goto :process_adaptive

    :check_default_settings
    const/16 v3, 0x64

    if-ne v1, v3, :process_adaptive

    if-nez v2, :process_adaptive

    goto :draw_original

    :process_adaptive
    move-object v3, p0

    check-cast v3, Landroid/graphics/drawable/AdaptiveIconDrawable;

    if-nez v0, :process_custom_shape

    invoke-virtual {v3}, Landroid/graphics/drawable/AdaptiveIconDrawable;->getForeground()Landroid/graphics/drawable/Drawable;

    move-result-object v4

    if-eqz v4, :draw_default_masked

    invoke-virtual {v4}, Landroid/graphics/drawable/Drawable;->getBounds()Landroid/graphics/Rect;

    move-result-object v5

    iget v6, v5, Landroid/graphics/Rect;->left:I

    iget v7, v5, Landroid/graphics/Rect;->top:I

    iget v8, v5, Landroid/graphics/Rect;->right:I

    iget v9, v5, Landroid/graphics/Rect;->bottom:I

    invoke-static {v4, v5, v1, v2}, Lcom/android/launcher3/ModShape;->adjustForegroundBounds(Landroid/graphics/drawable/Drawable;Landroid/graphics/Rect;II)V

    :draw_default_masked
    invoke-virtual {p0, p1}, Landroid/graphics/drawable/Drawable;->draw(Landroid/graphics/Canvas;)V

    if-eqz v4, :draw_default_return

    invoke-virtual {v4, v6, v7, v8, v9}, Landroid/graphics/drawable/Drawable;->setBounds(IIII)V

    :draw_default_return
    return-void

    :process_custom_shape
    invoke-virtual {p0}, Landroid/graphics/drawable/Drawable;->getBounds()Landroid/graphics/Rect;

    move-result-object v4

    invoke-virtual {v4}, Landroid/graphics/Rect;->width()I

    move-result v5

    int-to-float v5, v5

    iget v6, v4, Landroid/graphics/Rect;->left:I

    int-to-float v6, v6

    iget v7, v4, Landroid/graphics/Rect;->top:I

    int-to-float v7, v7

    invoke-virtual {p1}, Landroid/graphics/Canvas;->save()I

    move-result v8

    invoke-static {v0, v6, v7, v5}, Lcom/android/launcher3/ModShape;->makePath(IFFF)Landroid/graphics/Path;

    move-result-object v9

    invoke-virtual {p1, v9}, Landroid/graphics/Canvas;->clipPath(Landroid/graphics/Path;)Z

    const/high16 v9, 0x3e800000    # 0.25f

    mul-float/2addr v9, v5

    float-to-int v9, v9

    iget v10, v4, Landroid/graphics/Rect;->left:I

    iget v11, v4, Landroid/graphics/Rect;->top:I

    iget v12, v4, Landroid/graphics/Rect;->right:I

    iget v13, v4, Landroid/graphics/Rect;->bottom:I

    sub-int/2addr v10, v9

    sub-int/2addr v11, v9

    add-int/2addr v12, v9

    add-int/2addr v13, v9

    invoke-virtual {v3}, Landroid/graphics/drawable/AdaptiveIconDrawable;->getBackground()Landroid/graphics/drawable/Drawable;

    move-result-object v9

    if-eqz v9, :cond_background_done

    invoke-virtual {v9, v10, v11, v12, v13}, Landroid/graphics/drawable/Drawable;->setBounds(IIII)V

    invoke-virtual {v9, p1}, Landroid/graphics/drawable/Drawable;->draw(Landroid/graphics/Canvas;)V

    :cond_background_done
    invoke-virtual {v3}, Landroid/graphics/drawable/AdaptiveIconDrawable;->getForeground()Landroid/graphics/drawable/Drawable;

    move-result-object v9

    if-eqz v9, :cond_foreground_done

    new-instance v4, Landroid/graphics/Rect;

    invoke-direct {v4, v10, v11, v12, v13}, Landroid/graphics/Rect;-><init>(IIII)V

    invoke-static {v9, v4, v1, v2}, Lcom/android/launcher3/ModShape;->adjustForegroundBounds(Landroid/graphics/drawable/Drawable;Landroid/graphics/Rect;II)V

    invoke-virtual {v9, p1}, Landroid/graphics/drawable/Drawable;->draw(Landroid/graphics/Canvas;)V

    :cond_foreground_done
    invoke-virtual {p1, v8}, Landroid/graphics/Canvas;->restoreToCount(I)V

    return-void

    :draw_original
    invoke-virtual {p0, p1}, Landroid/graphics/drawable/Drawable;->draw(Landroid/graphics/Canvas;)V
    :try_end_0
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_0} :catch_0

    return-void

    :catch_0
    move-exception v0

    return-void
.end method"""

helper_method = r""".method public static adjustForegroundBounds(Landroid/graphics/drawable/Drawable;Landroid/graphics/Rect;II)V
    .locals 11

    # Scale the foreground around its center; inset is a percentage of each edge.
    iget v0, p1, Landroid/graphics/Rect;->right:I
    iget v1, p1, Landroid/graphics/Rect;->left:I
    sub-int v0, v0, v1
    int-to-float v0, v0

    const/high16 v1, 0x3f000000    # 0.5f
    mul-float v1, v0, v1

    int-to-float v2, p2
    const/high16 v3, 0x42c80000    # 100.0f
    div-float/2addr v2, v3
    mul-float/2addr v1, v2

    int-to-float v4, p3
    mul-float v4, v0, v4
    div-float/2addr v4, v3
    sub-float/2addr v1, v4

    iget v5, p1, Landroid/graphics/Rect;->left:I
    iget v6, p1, Landroid/graphics/Rect;->right:I
    add-int v5, v5, v6
    int-to-float v5, v5
    const/high16 v6, 0x40000000    # 2.0f
    div-float/2addr v5, v6

    sub-float v7, v5, v1
    float-to-int v7, v7
    add-float v8, v5, v1
    float-to-int v8, v8

    iget v0, p1, Landroid/graphics/Rect;->bottom:I
    iget v2, p1, Landroid/graphics/Rect;->top:I
    sub-int v0, v0, v2
    int-to-float v0, v0

    const/high16 v1, 0x3f000000    # 0.5f
    mul-float v1, v0, v1

    int-to-float v2, p2
    const/high16 v3, 0x42c80000    # 100.0f
    div-float/2addr v2, v3
    mul-float/2addr v1, v2

    int-to-float v4, p3
    mul-float v4, v0, v4
    div-float/2addr v4, v3
    sub-float/2addr v1, v4

    iget v5, p1, Landroid/graphics/Rect;->top:I
    iget v6, p1, Landroid/graphics/Rect;->bottom:I
    add-int v5, v5, v6
    int-to-float v5, v5
    const/high16 v6, 0x40000000    # 2.0f
    div-float/2addr v5, v6

    sub-float v9, v5, v1
    float-to-int v9, v9
    add-float v10, v5, v1
    float-to-int v10, v10

    invoke-virtual {p0, v7, v9, v8, v10}, Landroid/graphics/drawable/Drawable;->setBounds(IIII)V

    return-void
.end method"""

smali = root / "smali/com/android/launcher3/ModShape.smali"
text = smali.read_text()
text, count = re.subn(r"(?s)\.method public static draw\(Landroid/graphics/drawable/Drawable;Landroid/graphics/Canvas;Landroid/content/Context;\)V.*?\.end method", draw_method, text, count=1)
if count != 1:
    raise SystemExit("Could not replace ModShape.draw")
if ".method public static adjustForegroundBounds(" not in text:
    text = text.replace(".method public static makePath(IFFF)Landroid/graphics/Path;", helper_method + "\n\n.method public static makePath(IFFF)Landroid/graphics/Path;", 1)
smali.write_text(text)

prefs = root / "res/xml/launcher_preferences.xml"
text = prefs.read_text()
anchor = '<com.android.launcher3.widget.CustomListPreference android:persistent="true" android:entries="@array/mod_icon_shape_entries" android:title="Icon shape" android:key="mod_icon_shape" android:summary="%s" android:defaultValue="0" android:entryValues="@array/mod_icon_shape_values" />'
addition = anchor + '\n        <com.android.launcher3.widget.CustomListPreference android:persistent="true" android:entries="@array/mod_icon_zoom_entries" android:title="Icon foreground zoom" android:key="mod_icon_zoom" android:summary="%s" android:defaultValue="100" android:entryValues="@array/mod_icon_zoom_values" />\n        <com.android.launcher3.widget.CustomListPreference android:persistent="true" android:entries="@array/mod_icon_inset_entries" android:title="Icon safe-zone padding" android:key="mod_icon_inset" android:summary="%s" android:defaultValue="0" android:entryValues="@array/mod_icon_inset_values" />'
if "mod_icon_zoom" not in text:
    if anchor not in text:
        raise SystemExit("Could not find Icon shape preference insertion point")
    text = text.replace(anchor, addition, 1)
prefs.write_text(text)

arrays = root / "res/values/arrays.xml"
text = arrays.read_text()
array_block = """    <string-array name="mod_icon_zoom_entries">
        <item>80%</item><item>90%</item><item>100%</item><item>110%</item><item>120%</item><item>130%</item>
    </string-array>
    <string-array name="mod_icon_zoom_values">
        <item>80</item><item>90</item><item>100</item><item>110</item><item>120</item><item>130</item>
    </string-array>
    <string-array name="mod_icon_inset_entries">
        <item>0%</item><item>2%</item><item>4%</item><item>6%</item><item>8%</item><item>10%</item><item>12%</item>
    </string-array>
    <string-array name="mod_icon_inset_values">
        <item>0</item><item>2</item><item>4</item><item>6</item><item>8</item><item>10</item><item>12</item>
    </string-array>
"""
if "mod_icon_zoom_entries" not in text:
    anchor = '    <string-array name="mod_indicator_entries">'
    if anchor not in text:
        raise SystemExit("Could not find array insertion point")
    text = text.replace(anchor, array_block + anchor, 1)
arrays.write_text(text)

prefs_smali = root / "smali/com/android/launcher3/ModPrefs.smali"
text = prefs_smali.read_text()
anchor = """    const-string v0, "mod_row_extra"

    invoke-virtual {v0, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z"""
addition = """    const-string v0, "mod_icon_zoom"

    invoke-virtual {v0, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    const-string v0, "mod_icon_inset"

    invoke-virtual {v0, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

""" + anchor
if "const-string v0, \"mod_icon_zoom\"" not in text:
    if anchor not in text:
        raise SystemExit("Could not find ModPrefs.onChanged insertion point")
    text = text.replace(anchor, addition, 1)
prefs_smali.write_text(text)

print("Applied Icon Lab foreground zoom and safe-zone padding controls.")
