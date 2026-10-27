# Feature implementation status

## Feature 1 — Icon Lab: icon shape chooser

**Source status:** Present in the patched source tree.
**Build status:** Included in the successful full-resource build.
**Device validation:** Not yet verified on the target device.

The chooser currently offers:
- System default (value 0; preserves normal drawable rendering)
- One UI-style squircle (value 1)
- Rounded square (value 2)
- Circle (value 3)

The implementation is connected from `BaseIconFactory` to `ModShape.draw`; shape clipping is applied to adaptive icons only when a non-default shape is selected. The `launcher_preferences.xml` source contains the Icon Lab category and `mod_icon_shape` preference, and the compiled APK resource table contains the shape entries/values.

### Build pipeline correction

The earlier workflow rebuilt only Smali while preserving the stock resource table. That dropped the patched settings XML and the new arrays, which explains why the new controls did not appear. The current full-source build compiles the patched resource table as well as DEX. A small build-preparation script replaces several Android-private framework references that block AAPT2 linking; the original source archive is not rewritten.

### Remaining work for this feature

- Install and confirm the Icon Lab category is visible.
- Change each shape and confirm icons update after launcher restart.
- Check non-adaptive icons and custom/random shapes retain their original rendering when System default is selected.
- Only after device verification should this feature be marked complete.

## Not yet implemented/verified

Foreground zoom/inset and safe-zone controls, per-app shape overrides, full icon-pack search/preview, expanded animation engines, Dock Studio beyond the existing controls, folder animation overrides, and home-screen multi-select remain separate work items. They must not be inferred from a successful APK build.
