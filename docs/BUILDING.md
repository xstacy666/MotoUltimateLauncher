# Build Moto Launcher APK in GitHub Actions

## One-time source upload

Place the previously prepared archive at:

`source/MotoLauncher3_Ultimate_patched_sources.zip`

The archive should contain the decoded Apktool project (including `apktool.yml` and the patched `decoded_v2/smali/com/android/launcher3/ModStack.smali`).

## Run the build

1. Open **Actions** in this repository.
2. Select **Build Moto Launcher APK**.
3. Choose **Run workflow** on `main`.
4. When complete, open the workflow run and download **MotoLauncher3-Ultimate-CI-build** under Artifacts.

The workflow uses Apktool's no-resource-rebuild mode to avoid reprocessing unusual OEM resource filenames. It creates a temporary CI signing key; that signature is for testing only and will not match Motorola's platform signature. Do not treat the output as a normal install/update for the preinstalled system launcher. Keep a recovery path before testing any system-level replacement.

## Current scope

This workflow builds the existing patched source archive. It does not magically implement missing features. Icon zoom/inset controls, new app-opening transitions, folder animations, and home-screen multi-select still need code-level implementation and on-device validation.
