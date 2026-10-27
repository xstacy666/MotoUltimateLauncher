# Decompiled-source findings and first Recents patch

The user-provided decoded tree was inspected locally. The source archive was not uploaded to this repository because it contains a large amount of decompiled third-party launcher code.

## Confirmed findings

- `smali/com/android/launcher3/ModStack.smali` reads `mod_recents_style` with a fallback value of `1`.
- `res/xml/launcher_preferences.xml` also declares the Recents style default as `1`.
- `res/values/arrays.xml` maps value `1` to “iOS stacked cards”.
- The `ModStack.params(1)` preset uses a 35-degree rotationY input. This is a plausible contributor to the reported excessive card tilt; it is a concrete code path, unlike generic rotation strings from bundled libraries.
- The same class applies rotationY, rotationX, view rotation and translationZ to Recents `TaskView` children when a non-stock style is selected.
- `ModShape.draw` reads `mod_icon_shape`, defaulting to 0; it only applies its custom clipping/re-draw path to `AdaptiveIconDrawable` when the value is non-zero. This supports the intended “preserve original shape by default” behavior for this code path.
- `ModIconPack` already contains a basic appfilter-based pack lookup and custom per-component bitmap lookup. It is not yet the full icon-pack control centre requested.

## First local patch prepared

The separate patch working copy changes:
1. Runtime fallback for `mod_recents_style`: 1 -> 0 (Stock/flat).
2. The first non-stock preset's rotationY input: 35 degrees -> 8 degrees.
3. The XML preference default: 1 -> 0.

This leaves the other selectable presets intact. Existing user-saved preference values may override defaults; selecting “Stock” in the launcher settings will also explicitly set the stored value to 0.

## Not yet complete

This is a narrow first patch, not the full feature request. Adaptive-icon toggles, zoom/padding controls, expanded icon pack UX, settings categorization, app-opening animations, multi-select/folder workflows and broader Dock Studio controls are not yet implemented. The patched source tree has not been rebuilt or device-tested. Do not install it as a privileged system replacement until the build, signature requirements, and rollback route have been verified.


## Follow-up analysis — icon pack and Recents integration

The decoded project already contains `com.android.launcher3.widget.ModIconPackPreference`, a package-discovery ListPreference that queries the legacy ADW, Nova, and Apex icon-pack actions. `ModIconPack.get()` reads the selected `mod_icon_pack` package, parses its `appfilter` XML, and resolves component-to-drawable mappings. The initial Icon Lab patch had been inserting a second free-text preference with the same key; that was incorrect. The patch now preserves the existing picker and inserts only the zoom and safe-zone controls.

The manifest originally queried only Motorola-specific actions. The build patch now adds explicit Android package-visibility queries for the icon-pack actions that the picker scans, which is important on modern Android versions.

The Recents hook was originally called from `RecentsView.onScrollChanged` only. The patch now also calls it after `onLayout` recalculates page offsets, so the selected style or Stock transform reset is reconciled after layout as well as scrolling. The patch does not write card X/Y positions or scale values; native Quickstep remains responsible for card placement and scale animation.

These are code-level fixes validated by the CI build and resource checks. They still require on-device confirmation that installed icon packs appear and apply, and that Recents cards no longer appear stuck/overlapped during open, swipe, dismiss, and return-home transitions.
