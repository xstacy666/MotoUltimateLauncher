# Build Moto Launcher APK in GitHub Actions

## Build input

The build workflow uses:

- `source/MotoLauncher3_Ultimate_Patched_All.zip` — the complete decoded Apktool project.
- The archive must contain `apktool.yml`, Smali sources, and `ModStack.smali`.

## Run the build

1. Open **Actions** in this repository.
2. Select **Build Moto Launcher APK (full patched source)**.
3. Choose **Run workflow**, or push a change under `source/**` or to the workflow file.
4. Download **MotoLauncher3-Ultimate-Patched-CI-build** from the completed run.

The workflow extracts and builds the entire Apktool project with `apktool b --no-res`, rather than copying only one Smali file into a separately decoded stock APK. It signs with an ephemeral CI test key, verifies the signature and checks the package name, then publishes a build report with the APK SHA-256 and DEX inventory.

## Important status and limitations

**A successful build is not proof that the requested feature set is implemented or works on a device.** The existing feature specification remains a plan until code changes are present in the actual launcher code and tested. In particular, icon zoom/insets, icon-pack controls, Dock Studio, OEM-inspired animation choices, folders/multi-select, and Recents repair must not be treated as complete just because the APK builds.

The CI signature is not Motorola's platform signature. Do not replace the system launcher or flash this APK without a verified backup and a recovery path. A package/signature check also does not prove device installability or runtime stability; those require testing on the target Motorola Edge 50 Pro / Android 16 build.
