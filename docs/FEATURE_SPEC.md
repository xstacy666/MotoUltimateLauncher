# Moto Launcher Ultimate — Feature & Implementation Specification

Status: implementation plan grounded in the supplied APK audit; **not yet implemented in a rebuilt APK**.

## Product invariants

1. **Shape preservation is the default.** If a user chooses a custom/random shape or an icon-pack-provided shape, do not silently replace it with a launcher-wide mask. Every masking operation is explicitly opt-in.
2. **Independent controls stay independent.** Masking, adaptive-icon handling, foreground zoom, icon size, safe-zone/padding, background treatment, and per-app overrides must not unexpectedly overwrite each other.
3. **Safe recovery first.** Keep the original APK untouched, build to a separate output, verify package/signing/installability, and provide a reversible install/rollback path before testing on the daily-use device.
4. **OEM-style animation choices are original approximations**, not copied proprietary implementations or claims of exact OEM parity. Android version, launcher architecture, and system animation settings can limit what the launcher controls.

## Settings information architecture

Use a searchable Settings landing page with categories and a consistent reset-to-default action:

- **Personalization** — theme, wallpaper-derived colors, light/dark/system, accent, icon labels, typography.
- **Icons & Icon Packs** — shape preservation, adaptive masks, scaling, padding, icon packs, overrides.
- **Home Screen** — grid, rows/columns, icon size, labels, widgets, page indicator, transitions, portrait/landscape.
- **App Drawer** — grid, search, tabs/categories, sorting, hidden apps, suggested apps, scroll behavior.
- **Dock Studio** — dock visibility, dimensions, margins, icon count/size/spacing, corner radius, opacity, color, blur/glass where platform supports it.
- **Folders & Selection** — folder appearance, open/close behavior, multi-select, batch actions.
- **Gestures & Shortcuts** — swipe up/down, double tap, pinch, long press, back/home-related shortcuts where allowed.
- **Animations** — app launch, close/return, folder, page, drawer, icon removal, reduced-motion and performance options.
- **Recents / Overview** — only settings the launcher can legitimately control; overview rendering may be owned by the system Quickstep implementation.
- **Backup & Restore** — export/import settings and layout; validate backups before applying.
- **Performance & Diagnostics** — cache refresh, safe mode, diagnostics, animation scale, low-memory presets.
- **About & Recovery** — version/build info, restart launcher, reset preferences, export diagnostics, rollback instructions.

Every setting should have a clear label, concise explanation, safe default, and persisted value. Search results should deep-link to the relevant setting. Hide/disable controls when the Android API or device build cannot support them rather than showing fake toggles.

## Icon shape and adaptive icon system

### Shape-preservation mode
- Default: **Preserve source shape**. Do not apply an additional launcher mask to custom, random, or icon-pack-provided artwork.
- Options: Preserve source; use adaptive foreground/background as provided; apply selected mask; mask only legacy icons (if feasible).
- Preview selected shape on a sample grid before applying.
- Do not treat the launcher icon-shape setting as permission to mutate source bitmap/vector assets.

### Adaptive icon controls
- Master toggle for launcher-side masking, default off.
- Mask picker: available system/resource shapes and supported custom shapes.
- Separate foreground scale/zoom slider with reset.
- Horizontal and vertical offsets if supported by the rendering path.
- Safe-zone/padding control.
- Optional background fill/transparency behavior where source format supports it.
- Per-app overrides: inherit global, preserve original, adaptive, mask with selected shape, custom icon.
- One-tap reset for an app and reset-all with confirmation.
- Preview state must match the actual icon renderer; do not claim support for masks that are not wired into rendering.

### Compatibility notes
Adaptive icons are structured foreground/background assets. Arbitrary raster icons and icon-pack drawables may not expose those layers. For those assets, preserve the original image unless the user explicitly requests a mask. Avoid double-masking and clipping important foreground details.

## Icon pack control centre

- Installed pack discovery and explicit pack selection.
- Search packs and search icons by app label/package.
- Pack details, icon count when available, preview grid, missing-icon report.
- Apply, revert, reset, and refresh launcher icon cache.
- Per-app icon replacement from a pack; custom image selection only if the app's storage/picker architecture supports it.
- Unmatched-icon handling: preserve original, use pack fallback, or use a chosen fallback.
- Manual mapping editor with package/activity identification.
- Preview before commit; undo last mapping; reset one mapping or all mappings.
- Cache invalidation after pack changes, app installs/uninstalls, and mapping changes.
- Clear diagnostics for unsupported pack formats, missing resources, and duplicate mappings.
- Do not require internet access for locally installed packs.

## App launch and launcher animation chooser

Provide a previewable list with duration, intensity, and reduced-motion controls. Candidate original animation profiles:

- Classic / stock fade-scale
- Subtle scale-up + fade
- Spring pop
- Material-style shared-axis approximation
- Meizu/Flyme-inspired soft zoom
- OPPO/ColorOS-inspired fluid zoom
- Samsung/One UI-inspired gentle scale
- Xiaomi/MIUI/HyperOS-inspired elastic zoom
- iOS-inspired spring zoom
- Slide-up, slide-from-edge, fade-through, and no-animation

These are inspiration labels for original generic effects, not OEM code. Use platform-supported activity/launcher transitions and app-launch callbacks; do not promise control over transitions that the OS or target app owns. Add a live preview, reset button, speed presets (slow/normal/fast), and reduced-motion override.

## Home-screen multi-select and folders

- Enter selection mode by long-pressing an icon then selecting more icons, with clear selection count and cancel affordance.
- Batch actions: create folder, move to page/folder if supported, remove from home (not uninstall), hide/disable only where supported, and choose a pack icon for selected apps.
- Confirm destructive or ambiguous actions; distinguish **Remove from home** from **Uninstall**.
- Folder creation from multiple selected apps; folder naming, icon preview, open/close animation, grid, background/shape, and restore-on-undo.
- Support drag selection only if it can be implemented reliably; long-press + tap selection is the baseline.
- App removal animation presets inspired by MIUI-style dissolve/shrink/spring, implemented as original effects; never delay the actual operation in a way that risks stale workspace state.
- Undo toast for home removal and folder merge when possible.

## Dock Studio

- Enable/disable dock and choose fixed or adaptive number of slots if existing architecture supports it.
- Width, height, side margins, bottom inset, icon size, icon spacing, horizontal/vertical padding.
- Radius, fill color, opacity, border, optional shadow.
- Glass/blur/translucency modes with capability detection and a solid fallback.
- Presets: stock, compact, pill, glass, floating, minimal.
- Preview before applying; respect gesture navigation and display cutouts.
- Avoid expensive blur on low-memory/low-GPU devices; include performance fallback.

## Recents / Overview distortion — required investigation and acceptance criteria

The supplied screenshot shows cards at a severe 3D angle with distorted/reversed-looking content. The visible Clear all control is near the bottom. The APK string audit contains Quickstep/Recents-related identifiers, but strings alone do not prove which code path causes the transform.

Investigation sequence:
1. Decompile the launcher and identify the actual overview/task-view transform code and any custom mod hooks.
2. Trace rotationX/rotationY, perspective/camera distance, scale, task-card bounds, display rotation, and device posture/orientation.
3. Check whether a custom Recents style or stale preference enables a 3D transform; test defaults and reset the relevant preference.
4. Prefer a stable, near-flat card layout: rotationX/rotationY at zero unless the user explicitly chooses a supported subtle effect; avoid negative/invalid scale and excessive perspective.
5. Keep task-card content upright and clipped to rounded card bounds; ensure gestures and system navigation remain intact.
6. Position Clear all at the bottom of the task stack/overview area, above the gesture handle and insets, without overlap; preserve portrait and landscape layouts.
7. Test 0/90/180/270-degree rotations, gesture navigation, multiple tasks, empty recents, and screen-size/font/display-scale changes.

Acceptance: cards render upright without extreme skew or mirrored text; task switching and swipe dismissal work; Clear all is visible, reachable, and not overlapped by the gesture bar; no crash or stuck overview state. If Overview is implemented in a privileged/system Quickstep component, do not claim a normal launcher-only update can fix it until the actual owning component is confirmed.

## Restart, recovery, and diagnostics

- “Restart launcher” should use a supported safe mechanism: restart the launcher process/activity or relaunch the home activity, depending on platform constraints. Warn that widgets may briefly reload.
- Never bind-mount over a system APK as the first install path.
- Preserve original APK and checksum; create a backup before any device-level replacement.
- Validate package name, manifest, resource compilation, DEX verification, APK alignment, signature/install policy, and target Android compatibility.
- If platform signing/privileged permissions are required, document the exact limitation; do not imply a re-signed APK can replace a platform-signed system app.
- Safe mode disables custom icon rendering/animations and loads conservative defaults.
- Diagnostics export version, Android build, selected settings, and relevant errors; do not export personal app data.
- Settings reset, cache clear, and app-data clear must be clearly distinguished.

## Additional feature backlog

- Home and drawer grid presets; separate portrait/landscape values.
- Label visibility, font size, line count, icon-label spacing.
- Page transitions, infinite scroll toggle, page indicator customization.
- Drawer sorting: name, install/update time where available, most-used only with privacy-conscious local tracking.
- Hidden apps and app drawer folders/categories.
- Gesture action assignment with conflict warnings.
- Wallpaper-based colors and contrast-safe presets.
- Folder size/grid, background, label, and open animation.
- Backup/restore of layout and preferences with schema versioning.
- Animation budget and low-end-device preset.
- Reset one category, reset one setting, reset all.
- Feature availability diagnostics and settings search.
- Import/export icon mappings.
- Accessibility: reduced motion, adequate touch targets, contrast, screen-reader labels.

## Build and test gates

Do not call this complete until all gates pass:
1. Source/resource decompilation is usable and changes are tied to identifiable classes/resources.
2. Changes are made in a working copy; original APK hash remains unchanged.
3. Rebuild succeeds and the package is structurally valid.
4. Signing and install route are documented for this exact Motorola Android 16 build.
5. Static verification passes; then test on a spare/test device or reversible setup before daily-driver use.
6. Smoke tests cover cold start, home, drawer, folders, icon pack changes, orientation, widget restore, app launch, Recents, restart, and rollback.

Current status: the APK has only been audited and triaged. This specification is not evidence that the features have been implemented.
