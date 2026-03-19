#!/usr/bin/env python3
"""
Generate web-images/images.json from the contents of the web-images/ directory.
Run from the repo root:  python generate_manifest.py
Re-run whenever you add or remove images.
"""
import json, os, sys

IMG_DIR = "web-images"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

if not os.path.isdir(IMG_DIR):
    print(f"Error: '{IMG_DIR}' directory not found. Run from the repo root.")
    sys.exit(1)

images = sorted(
    f for f in os.listdir(IMG_DIR)
    if os.path.splitext(f)[1].lower() in EXTENSIONS
)

out_path = os.path.join(IMG_DIR, "images.json")
with open(out_path, "w") as fp:
    json.dump(images, fp, indent=2)

print(f"Wrote {len(images)} entries to {out_path}")
