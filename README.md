# Moto Launcher Ultimate

A customization and recovery project for Motorola Launcher 3, targeting the Motorola Edge 50 Pro on Android 16.

> **Status: early project setup.** This repository starts with planning and audit documentation. No rebuilt or device-tested APK is claimed yet.

## Goals

- Preserve existing launcher behavior and custom modifications wherever possible.
- Diagnose and fix distorted, extreme-3D Recents/Overview cards.
- Expand icon handling: adaptive icons, optional masks, scaling/padding, icon-pack selection, search/preview, and per-app overrides.
- Organize launcher settings into clear, searchable categories.
- Add Dock Studio controls for background, blur/glass styling, dimensions, margins, corner radius, opacity, icon sizing, and spacing.
- Add home-screen and app-drawer grid, labels, folders, search, sorting, and gesture controls.
- Add original app-opening animation presets inspired by common OEM design patterns, within Android platform limits.
- Add settings backup/restore, diagnostics, cache reset, launcher restart, and safe-recovery options.

## Device / platform target

- Device: Motorola Edge 50 Pro
- Android: Android 16
- Package string observed in initial archive audit: `com.motorola.launcher3`
- Version-name string observed in initial archive audit: `16-mod-final`

These strings are archive observations, not proof that the APK installs or works.

## Repository layout

- `docs/ROADMAP.md` — staged implementation plan and acceptance criteria
- `docs/APK_AUDIT.md` — initial binary audit and known limitations
- `docs/SAFETY.md` — backup, installation, rollback, and signing cautions

## Safety

Do not install a modified launcher system APK until its signature, Android version compatibility, target path, and rollback plan are verified. Recents/Overview may be controlled by System UI/Quickstep and Motorola framework code, not only launcher resources.

## Next steps

1. Establish exact APK inputs and record hashes.
2. Identify source lineage and licensing obligations.
3. Set up Android reverse-engineering/build tooling.
4. Reproduce and diagnose the Recents distortion before making a narrow fix.
5. Implement features incrementally and test on the target device.

No feature is complete until implemented, built, and tested.
