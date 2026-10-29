# Uploaded APK audit (local attachment)

This report records the APK inspected during the ChatGPT task. It does **not** claim that the binary has been committed to this repository or that a full Apktool decompilation has been completed.

- Filename supplied in the working session: `com.motorola.launcher3.apk`
- File size: `17,597,499` bytes
- SHA-256: `7f226260009252f7ae017d30e3471188b0a0a9f42c8582317210f18b90b25807`
- DEX files: `classes.dex`, `classes2.dex`, `classes3.dex`
- `apktool.yml`: absent (this is an APK, not an already decoded Apktool project)

## Preliminary DEX string triage

Static string extraction from the DEX files found references including:

- `com/android/launcher3/ultimate/ModAnim`, `ModRecents`, `ModDock`, `ModPages`, `ModDelete`, and `ModBlur`
- `com/android/launcher3/ultimate/IconBrowser` and `UltimateScreen`
- `mod_icon_pack`, `mod_icon_pack2`, `mod_icon_pack_enabled`, `mod_icon_pack_calendar`, and `mod_icon_pack_shape`
- UI strings including `Moto Ultimate`, `Choose an icon pack`, and `Icons & icon packs`

These are preliminary strings from DEX data, not proof that each feature is wired correctly or functional. A full decode with Apktool is needed for smali/resources, followed by targeted code inspection and a build/test cycle.

## Repository follow-up required

The repository currently contains APK assets with different size metadata from this local attachment. To ensure the decompile artifact is for this exact file, add this APK to the repository as `source/com.motorola.launcher3.apk` (confirming the SHA-256 above), then run **Actions → Decompile Launcher APK**. The workflow artifact will preserve the input hash alongside the decoded output.
