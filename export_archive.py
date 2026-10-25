#!/usr/bin/env python3
"""
Snapshot the submitted constellations from Firestore/Storage into archive/.
Writes archive/constellations.json (plus constellations.js, for opening the site from disk) and downloads each image to archive/constellations/.
Run from the repo root:  python export_archive.py
Uses the public Firestore REST API, so no credentials are needed.
"""
import json, os, sys, urllib.request

PROJECT = "galactic-constellations"
LIST_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents/constellations?pageSize=300"
OUT_DIR = "archive"
IMG_DIR = os.path.join(OUT_DIR, "constellations")


def fetch_json(url):
    with urllib.request.urlopen(url) as r:
        return json.load(r)


def field(fields, key):
    v = fields.get(key, {})
    return next(iter(v.values()), None)


if not os.path.isdir("web-images"):
    print("Error: run from the repo root.")
    sys.exit(1)
os.makedirs(IMG_DIR, exist_ok=True)

docs, token = [], None
while True:
    data = fetch_json(LIST_URL + (f"&pageToken={token}" if token else ""))
    docs += data.get("documents", [])
    token = data.get("nextPageToken")
    if not token:
        break

entries = []
for doc in docs:
    f = doc["fields"]
    file_name = field(f, "fileName") or doc["name"].rsplit("/", 1)[-1]
    img_path = os.path.join(IMG_DIR, file_name)
    if not os.path.exists(img_path):
        try:
            urllib.request.urlretrieve(field(f, "imageUrl"), img_path)
        except Exception as e:
            print(f"Skipping {file_name}: {e}")
            continue
    entries.append({
        "constellationName": field(f, "constellationName"),
        "astronomerName": field(f, "astronomerName"),
        "sourceImage": field(f, "sourceImage"),
        "fileName": file_name,
        "upvotes": int(field(f, "upvotes") or 0),
        "downvotes": int(field(f, "downvotes") or 0),
        "createdAt": field(f, "createdAt") or doc.get("createTime"),
    })

out_path = os.path.join(OUT_DIR, "constellations.json")
with open(out_path, "w", encoding="utf-8") as fp:
    json.dump(entries, fp, indent=2, ensure_ascii=False)

with open(os.path.join(OUT_DIR, "constellations.js"), "w", encoding="utf-8") as fp:
    fp.write("window.ARCHIVE_ENTRIES = " + json.dumps(entries, indent=2, ensure_ascii=False) + ";\n")

print(f"Wrote {len(entries)} of {len(docs)} entries to {out_path} and constellations.js")
