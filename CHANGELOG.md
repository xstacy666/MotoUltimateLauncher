# Changelog

## Alpha pre-release — KSU module packaging

- Added a reproducible GitHub Actions workflow to package a KernelSU ZIP from the repository APK.
- Uses the OEM launcher directory and filename for the systemless replacement.
- Adds bind-mount logging, source/target verification, and an uninstall cleanup hook.
- Documents stale mount cleanup: remove older module and reboot before testing this build.
- Clarifies known limitations and feature status; no unverified launcher features are claimed as complete.

### Known limitations

- Experimental and intended primarily for Motorola Edge 50 Pro / Android 16.
- The APK's signature compatibility and runtime behavior must be tested on-device.
- Uninstall hooks cannot guarantee cleanup in every mount namespace; reboot after removal.
- This is a module packaging pre-release, not a verified feature-complete launcher build.
