# Build Moto Launcher APK in GitHub Actions

## Build input

The workflow uses `source/MotoLauncher3_Ultimate_Patched_All.zip`, a decoded Apktool project containing the launcher Smali and resource XML. It must include `apktool.yml`, the launcher classes, and the patched `res/xml/launcher_preferences.xml`.

## Run the build

1. Open **Actions** in this repository.
2. Select **Build Moto Launcher APK (full patched source)**.
3. Choose **Run workflow**, or push a change under `source/**`, `tools/**`, or to the workflow file.
4. Download `MotoLauncher3-Ultimate-Patched-CI-build` from the completed run.

The workflow builds the **complete patched project**, including its resource table and settings XML. It runs `tools/prepare_resource_build.sh` to replace a few private Android-framework references that block AAPT2 linking in the generic CI framework, then checks that the compiled APK contains the Icon Lab shape arrays and the Icon Lab/Dock Studio preference entries. It signs with an ephemeral CI test key, verifies the signature and package name, and publishes a build report.

## Feature status

See `docs/FEATURE_IMPLEMENTATION_STATUS.md` for the per-feature status. Feature 1 is the existing Icon Lab shape chooser (System default, One UI-style squircle, rounded square, and circle). The successful build confirms that its code and settings resources are packaged; **it does not prove the settings appear or the shapes behave correctly on a device**.

Foreground zoom/inset controls, per-app shape overrides, expanded icon-pack search/preview, new animation engines, folder animation overrides, home-screen multi-select, and full Recents validation remain separate work items. Do not infer those features from a green CI run.

## Device safety

The CI signature is not Motorola's platform signature. Do not replace the system launcher or flash this APK without a verified backup and recovery path. A valid signature and package name do not establish system installability, platform-signature privileges, or runtime stability on the target Motorola Edge 50 Pro / Android 16 build.
