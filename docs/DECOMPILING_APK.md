# Decompiling a launcher APK

Use **Actions → Decompile Launcher APK → Run workflow**.

1. The input APK must already exist in the checked-out repository. The default is `source/com.motorola.launcher3.apk`.
2. Select resource decoding to produce decoded resources and smali, or disable it for a faster no-resource decode.
3. Download the `launcher-decompiled-*` artifact from the completed run. It contains the Apktool output and an input SHA-256 audit.

## Important limitation

Apktool produces decoded Android resources and smali, not the original Java/Kotlin source. The input APK is not modified, re-signed, or installed. Check the artifact's SHA-256 before treating it as a decompile of a specific APK.

To decompile a newer APK, first commit that exact APK at a repository path (or replace the default source APK), then run the workflow with that path. The workflow cannot access APK files attached only to a ChatGPT conversation.
