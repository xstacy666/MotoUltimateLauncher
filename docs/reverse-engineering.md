# Launcher reverse-engineering workflow

This repository uses reverse-engineering tools to investigate its own launcher APK and compare decompiled behavior with the patch scripts. The [awesome-reverse-engineer-anything list](https://github.com/AIshihzong/awesome-reverse-engineer-anything) is a catalogue, not a patching engine. The practical Android tools selected for this project are:

- [JADX](https://github.com/skylot/jadx): inspect DEX as approximate Java source.
- [Apktool](https://github.com/iBotPeaches/Apktool): decode resources and smali.
- [REA](https://github.com/morluto/rea): optional agent/MCP workflow for evidence-led investigation across supported binary-analysis backends.

## Run a repeatable local analysis

Install Java, JADX, and Apktool from their official releases. Then run:

```bash
bash tools/analyze_launcher_apk.sh /path/to/MotoLauncher3-Ultimate-CI-signed.apk
```

Or choose an output directory:

```bash
bash tools/analyze_launcher_apk.sh /path/to/launcher.apk ./analysis/launcher-test
```

The script verifies the APK container, records its SHA-256 and tool versions, decodes resources/smali, decompiles DEX, and collects candidate references to Recents/task-view transforms and icon-pack settings. It refuses to overwrite an existing output directory and never patches, signs, or installs the APK.

## Use the results for the current bugs

1. Start with the generated REPORT.md and search hits for RecentsView, TaskView, translationZ, rotationX, ModPrefs, and IconPack.
2. Trace each hit into both the decompiled Java and corresponding smali/resources. Decompiled Java can be incomplete or misleading.
3. Compare the findings against tools/apply_recents_dock_fixes.py and tools/apply_icon_lab_zoom_controls.py. Patch the source/patch script, not generated decompiler output, whenever possible.
4. Rebuild with the existing GitHub Actions workflow, then test Recents opening, horizontal swiping, dismissing tasks, returning home, and icon mapping on the target Android device. A successful build alone does not prove runtime correctness.

## Optional REA agent integration

REA is an optional local MCP/CLI investigation tool, not a library that should be bundled into the Android APK or run as an unconfigured CI step. Follow the official [REA installation guide](https://github.com/morluto/rea#quick-start) and review its proposed agent configuration before approving it. Keep any model-provider credentials in your local agent configuration or secret manager; never commit credentials to this repository.

Use REA to ask an evidence-focused question such as: “Trace the Recents task-view layout and animation path in this APK, cite the exact methods and bytecode evidence, identify which transforms are written and reset, and list uncertainties.” Then validate its findings against JADX, Apktool output, source patches, and on-device behavior.

## Safety and reproducibility

Only analyze APKs you are authorized to inspect. Keep the original APK unchanged and retain its hash. Decompiled code is evidence for investigation, not a guarantee of exact source reconstruction. Do not treat a text preference for an icon-pack package name as complete icon-pack implementation until installed-pack discovery, component mapping, fallback behavior, and live icon rendering are verified.
