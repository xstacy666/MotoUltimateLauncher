#!/usr/bin/env python3
"""Apply the independent Dock visibility fix without touching Recents code."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
matches = list(root.glob("smali*/com/android/launcher3/DockBlur.smali"))
if len(matches) != 1:
    raise SystemExit(f"Expected one DockBlur.smali, found {matches}")
path = matches[0]
text = path.read_text()
alpha_gate = re.compile(
    r"(?m)^    invoke-virtual .*->getAlpha\(\)F\s*\n"
    r"\s*move-result v1\s*\n"
    r"\s*const v2, 0x3c23d70a[^\n]*\n"
    r"\s*cmpg-float v2, v1, v2\s*\n"
    r"\s*if-ltz v2, :cond_7\s*\n"
)
updated, count = alpha_gate.subn(
    "    invoke-virtual {p0}, Landroid/view/View;->getAlpha()F\n\n    move-result v1\n",
    text,
    count=1,
)
if count == 0:
    if "const v2, 0x3c23d70a" not in text:
        print("Dock alpha gate already absent; no change needed.")
        raise SystemExit(0)
    raise SystemExit("Could not locate expected DockBlur alpha gate")
path.write_text(updated)
print("Applied Dock visibility fix; Recents classes were not modified.")
