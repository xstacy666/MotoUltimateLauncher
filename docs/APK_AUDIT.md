# Initial APK audit

## Artifact examined
- Filename reported in the working conversation: `MotoLauncher3_Ultimate.apk`
- SHA-256: `c29bfc1b7947f9d483f06e8e5deafd0d3b7e10e28563df08416822ac43a6493d`
- ZIP archive integrity check passed.
- Archive entries: 1,304
- `classes.dex`: 8,772,832 bytes
- `classes2.dex`: 2,193,928 bytes
- `resources.arsc`: 4,392,424 bytes
- Binary `AndroidManifest.xml`: 57,928 bytes
- Package string observed: `com.motorola.launcher3`
- Version-name string observed: `16-mod-final`
- JAR/v1 signature-related files were present. A jarsigner verification reported warnings; this is not equivalent to verifying Android APK Signature Scheme v2/v3/v4 with apksigner, nor does it establish runtime compatibility.

## Existing strings / identifiers observed
- `mod_dock_style`
- `mod_dock_pad_x`
- `mod_dock_pt`
- `mod_dock_pb`
- `mod_icon_pack`
- `mod_icon_shape`
- `mod_recents_style`
- `com.android.launcher3.DockBlur`
- `com.android.launcher3.graphics.IconShape$Squircle`
- `com.android.launcher3.graphics.IconShape$RoundedSquare`
- `com.android.launcher3.graphics.IconShape$Circle`
- `com.android.launcher3.graphics.IconShape$TearDrop`

These strings indicate names present in the archive, but do not prove the corresponding features are functional or correctly wired.

## Tooling limitations at audit time
The initial environment did not have `apktool`, `jadx`, `d2j-dex2jar`, `aapt/aapt2`, `apksigner`, `adb`, `baksmali`, or `apkanalyzer`; common Python APK parsing libraries were also absent. No decompilation, source reconstruction, rebuild, or device test was completed during that audit.

## Existing live-mount script risks
The provided script targeted `/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk`. It copies an APK to `/data/local/tmp` and bind-mounts it over that path in PID 1's mount namespace. It does not first preserve the original target APK, validate the APK signature, verify that the target path exists and matches this device, or provide a reliable rollback flow. Syntax validation alone does not establish safety. Do not execute it until the exact device setup and recovery path are confirmed.

## Next audit actions
1. Re-verify SHA-256 of the exact current APK input.
2. Verify signing certificate details using Android `apksigner`.
3. Decode resources and manifest with compatible tooling.
4. Decompile DEX and trace the `mod_recents_style` code path.
5. Compare against a trusted original build if available.
6. Establish a clean, reproducible build before editing code.
