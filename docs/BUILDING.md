# Build Moto Launcher APK in GitHub Actions

## Required inputs

The repository needs both files:

- `source/MotoLauncher3_Ultimate_Patched_All.zip` — the patched Apktool source archive.
- `source/MotoLauncher3_Ultimate.apk` — the original stock Motorola launcher APK used on the device.

Upload the stock APK to the exact path above. The source ZIP alone is not enough: it contains decoded resources, and rebuilding those resources fails on private or OEM-only Android resource references.

## Run the build

1. Open **Actions** in this repository.
2. Select **Build Moto Launcher APK**.
3. Choose **Run workflow** on `main` (or let the workflow run after uploading the stock APK).
4. When complete, open the run and download **MotoLauncher3-Ultimate-CI-build** under Artifacts.

The workflow decodes the stock APK with resources left untouched, copies the patched `ModStack.smali`, rebuilds, signs with a temporary CI test key, and verifies the signature. The CI signature will not match Motorola's platform signature. Keep a recovery path before testing any system-level replacement.

## Current scope

This workflow builds the existing Recents-style patch. It does not yet implement missing features such as icon zoom/inset controls, new app-opening transitions, folder animations, or home-screen multi-select; those still need code-level implementation and on-device validation.
