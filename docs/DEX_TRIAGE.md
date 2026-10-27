# DEX triage — first pass

## Method
Performed a read-only ZIP integrity check and extracted string tables from `classes.dex` and `classes2.dex` in the APK whose SHA-256 is recorded in `APK_AUDIT.md`. This is preliminary triage, not decompilation.

## Recents / Quickstep clues in classes.dex
Strings include:
- `QuickstepLauncher`
- `mRecentsAnimationController`
- `mRecentsAnimationTargets`
- `mTaskViewSimulator`
- `mTransformParams`
- `mRecentsAnimationRunning`
- `mCurrentAppRotation`
- `mPreviousRotation`
- `finalTaskViewScaleX`
- `finalTaskViewScaleY`
- `mFakeTaskViewRect`
- `mTaskViewAnimatedRect`
- `mClearAllButton`
- `displayRotation`, `rotationHint`, and overview state strings

These indicate the APK includes Quickstep/Recents-related code and transform/rotation state. They do not identify the root cause by themselves.

## Related strings in classes2.dex
Strings include:
- `TaskView`
- `ClearAllButton`
- `ConstraintSet_android_rotationX`, `ConstraintSet_android_rotationY`
- `Constraint_android_rotationX`, `Constraint_android_rotationY`
- `Transform_android_rotationX`, `Transform_android_rotationY`
- `action_clear_all`, `action_clear_all_landscape`
- `clearAllAppsOverlayConfig`

The generic ConstraintLayout rotation strings may belong to bundled libraries and must not be mistaken for proof that Recents cards are explicitly rotated by custom code.

## Existing mod-related identifiers found
- `mod_recents_style`
- `mod_icon_pack`
- `mod_icon_shape`
- `mod_dock_style`
- `mod_dock_pad_x`
- `mod_dock_pt`
- `mod_dock_pb`
- `com/android/launcher3/DockBlur`
- `com/android/launcher3/graphics/IconShape` and shape classes for Circle, Squircle, TearDrop, RoundedSquare

These prove the identifiers are present in the DEX/resource string pool; they do not prove a setting is wired correctly.

## Next technical step
Use JADX to decompile DEX to Java-like source and Apktool to decode manifest/resources. Search for the implementation and call sites of `mod_recents_style`, `mTaskViewSimulator`, `finalTaskViewScaleX/Y`, and the icon-shape preference before making any behavior changes.

## Status
No DEX instructions or resources have been modified. No rebuilt APK has been produced. The next step requires decompilation/rebuild tooling that was not installed in the workspace during this first pass.
