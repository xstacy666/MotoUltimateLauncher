# Safety and rollback notes

- Keep an untouched copy of the original launcher APK outside the system partition.
- Record the device's exact build fingerprint and launcher package/path before making changes.
- Confirm a working recovery method before changing a privileged launcher.
- An APK that passes ZIP validation is not necessarily installable or compatible.
- JAR signature verification does not validate modern Android APK signing schemes.
- Avoid replacing a privileged system launcher with an APK signed by an unrelated key; signature or privileged-permission mismatches may cause failures.
- Prefer a reversible user-space test build when possible.
- Test one change at a time and record hashes, logs, and outcomes.
- Understand mount namespaces and reboot behavior before any live bind mount. Do not rely on an untested script for recovery.
- Export user settings before testing settings migrations or backup/restore.
