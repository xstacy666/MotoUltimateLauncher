# Øpium • Moto Ultimate Launcher

**Alpha / pre-release** — KernelSU systemless replacement module for the Motorola Edge 50 Pro on Android 16.

> ⚠️ Experimental. This release has not been confirmed working across devices or ROM variants. Back up first and keep a recovery path.

## Alpha module package

Use GitHub Actions → **Package KSU Alpha Module** to build a ZIP from `source/com.motorola.launcher3.apk`. Download the `opium-moto-ultimate-ksu-alpha` workflow artifact. This is an Actions artifact, not a published GitHub Release asset.

## Target
- Device: Motorola Edge 50 Pro
- Android: 16 (other versions unverified)
- Package: `com.motorola.launcher3`
- OEM path: `/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk`
- Module ID: `opium_moto_ultimate_launcher`

## Install
1. Keep the stock launcher APK and a recovery method available.
2. Remove any older version of this module and reboot before installing this build. This clears stale bind mounts from older scripts.
3. Install the generated ZIP in KernelSU and reboot.
4. Inspect `/data/adb/modules/opium_moto_ultimate_launcher/service.log` as root.
5. Verify the source and destination in `/proc/1/mountinfo`; a successful mount alone does not prove the launcher loaded.

## Uninstall / rollback
Remove the module in KernelSU and reboot. The uninstall hook attempts to unmount its replacement; reboot is the reliable fallback for stale mounts or separate namespaces. If the launcher crashes, disable/remove the module and reboot.

## Current feature/mod status
- Systemless replacement at OEM path — module script implemented; device verification required.
- Mount logging and verification — included.
- Uninstall cleanup hook — included; reboot recommended.
- APK features — inherited from the repository APK; not independently validated by this module release.
- Recents/Overview fixes, extra icon-pack support, and advanced settings — not claimed complete without a tested APK build.

## Docs
- [Changelog](CHANGELOG.md)
- [APK audit](docs/APK_AUDIT.md)
- [Safety and rollback](docs/SAFETY.md)
- [Decompilation workflow](docs/DECOMPILING_APK.md)

## Signing warning
A replacement APK signed with a different certificate may be rejected or behave incorrectly as a privileged OEM system app. Check Package Manager and logcat; a successful bind mount is not proof of package acceptance. No feature is marked complete solely because a build or mount command succeeds.