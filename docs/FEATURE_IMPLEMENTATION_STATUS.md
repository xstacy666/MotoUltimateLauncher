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

## Feature 2 — Icon foreground zoom and safe-zone padding

**Source status:** Implemented in the build-time source patch.
**Build status:** Included in successful run [40470586168](https://github.com/xstacy666/MotoUltimateLauncher/actions/runs/40470586168); the APK resource check passed.
**Device validation:** Not yet verified on the target device.

The Icon Lab now adds:
- **Icon foreground zoom:** 80%, 90%, 100%, 110%, 120%, and 130%.
- **Icon safe-zone padding:** 0%, 2%, 4%, 6%, 8%, 10%, and 12%.

The controls apply to adaptive-icon foreground layers. The default shape path continues to use Android's adaptive-icon drawing/mask path; custom shapes use the selected custom clip path. Changes to either preference clear the icon cache and restart the launcher process through the existing preference-change handler.

Validation still required on-device:
- Confirm both settings appear and persist.
- Verify zoom and padding change only the foreground, not the background layer.
- Check no clipping, distorted bounds, or crashes for System default and each custom shape.
- Confirm icon packs and non-adaptive icons remain unaffected.

## Not yet implemented/verified

Foreground zoom/inset and safe-zone controls, per-app shape overrides, full icon-pack search/preview, expanded animation engines, Dock Studio beyond the existing controls, folder animation overrides, and home-screen multi-select remain separate work items. They must not be inferred from a successful APK build.
