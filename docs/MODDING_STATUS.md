# Modding kickoff status

## Confirmed baseline

- Input APK: `MotoLauncher3_Ultimate.apk`
- SHA-256 observed in the working environment: `c29bfc1b7947f9d483f06e8e5deafd0d3b7e10e28563df08416822ac43a6493d`
- ZIP integrity check: passed.
- Package string previously observed in the archive: `com.motorola.launcher3`
- Version-name string previously observed: `16-mod-final`

## Current status

The modding effort is approved and started. This commit records the baseline only; it does not claim that the APK has been decompiled, changed, rebuilt, installed, or tested.

At kickoff, the current workspace has Java and standard ZIP tools, but `apktool`, `jadx`, `aapt/aapt2`, `apksigner`, and `adb` are not currently available on PATH. Source/resource recovery must be completed before safely editing compiled launcher behavior.

## Work order

1. Preserve and verify the original APK.
2. Set up APK decompilation/resource tooling.
3. Inspect manifest, resource settings, and DEX code paths related to `mod_recents_style`, icon handling, and dock controls.
4. Diagnose Recents transforms before changing code.
5. Make a minimal reversible code/resource change.
6. Rebuild, verify Android APK signing, and test on the target Motorola Edge 50 Pro / Android 16.

## Safety

Do not use the old live-mount script until the exact target path, signing requirements, backup, and recovery route have been verified. The original APK remains unchanged.
