# Implementation roadmap

## Phase 0 — Reproducible baseline
- [ ] Record SHA-256 of the exact APK used on-device.
- [ ] Record device build fingerprint, Android version, launcher package/version, and privileged install status.
- [ ] Determine source lineage and licensing obligations.
- [ ] Set up and document compatible Android build/decompilation tools.
- [ ] Preserve the original and establish a baseline without replacing the daily launcher.

**Exit criteria:** baseline is reproducible or binary-only limitations are documented.

## Phase 1 — Recents / Overview distortion
- [ ] Capture a current screenshot and screen recording.
- [ ] Collect relevant logcat output while opening/closing Recents.
- [ ] Determine whether cards are rendered by Launcher3/Quickstep, System UI, or Motorola framework overlays.
- [ ] Inspect display density, rotation, task transforms, surface bounds, and custom Recents flags.
- [ ] Make the smallest reversible change that fixes the transform.
- [ ] Test gesture navigation, supported 3-button navigation, portrait/landscape, and repeated task switching.

**Exit criteria:** cards render at normal perspective and size, Clear All remains reachable, and task switching has no regression.

## Phase 2 — Icon engine
- [ ] Adaptive icon foreground/background handling.
- [ ] Independent toggles for mask application and adaptive icon treatment.
- [ ] Scale/zoom, inset/padding, and foreground alignment.
- [ ] Per-app overrides and reset-to-default.
- [ ] Icon-pack discovery, listing, preview, search, apply, and reset.
- [ ] Custom icon mapping and cache refresh.
- [ ] Regression tests for existing arbitrary icon silhouettes; do not force a global mask unless enabled.

## Phase 3 — Settings architecture
- [ ] Group settings into Home Screen, App Drawer, Icons, Dock Studio, Folders, Gestures, Animations, Appearance, Backup & Restore, and Diagnostics.
- [ ] Add settings search and sensible defaults.
- [ ] Add launcher restart with confirmation and safe fallback.
- [ ] Add export/import with schema versioning and validation.

## Phase 4 — Dock Studio and layout
- [ ] Dock background, glass/blur where supported, transparency, radius, dimensions, margins, padding, icon size, and spacing.
- [ ] Independent portrait and landscape layout profiles where supported.
- [ ] Home/app-drawer grid and label controls.
- [ ] Folder styling, sorting, and search.
- [ ] Theme / Material You integration only where compatible with device framework.

## Phase 5 — Opening animations
- [ ] Original presets inspired by broad design patterns: subtle zoom, spring, fade, slide, and blur-like transition.
- [ ] Respect Android transition APIs and system animation settings.
- [ ] Provide a safe default and disable option.
- [ ] Test app launch, return home, cold start, and low-memory behavior.

## Phase 6 — Hardening
- [ ] Diagnostics with app/version/build identifiers and safe log export.
- [ ] Cache reset with clear scope and confirmation.
- [ ] Backup/restore validation and failure recovery.
- [ ] Document performance toggles.
- [ ] Clean install, upgrade, rollback, and reboot tests.
- [ ] Release notes and known limitations.

## Acceptance principles
- No feature is complete until implemented, built, and tested.
- Never replace a system APK without a verified backup and recovery path.
- Keep platform-specific or privileged behavior separate from normal launcher customization.
