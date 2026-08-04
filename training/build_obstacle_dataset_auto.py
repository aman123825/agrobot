"""
FULLY AUTOMATED Obstacle Dataset Builder
=========================================
Uses Grounding DINO (zero-shot detection) to AUTO-ANNOTATE images
downloaded from free sources. NO MANUAL LABELING NEEDED.

Pipeline:
  1. Download images from Pexels/Unsplash (free, no API key needed for Unsplash)
  2. Run Grounding DINO to auto-detect and annotate bounding boxes
  3. Merge with COCO 2017 data for person/vehicle/animal
  4. Package as obstacle_dataset.zip

Requirements:
  pip install autodistill autodistill-grounding-dino \
              supervision Pillow tqdm pyyaml requests

Usage:
  python build_obstacle_dataset_auto.py

This takes ~30-60 min (mostly downloading images + running inference).
Requires a GPU for Grounding DINO (runs on Colab too!).
"""

import json
import os
import random
import shutil
import urllib.request
import zipfile
from pathlib import Path

import yaml

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

# ============================================================================
# CONFIG
# ============================================================================

SEED = 42
random.seed(SEED)

WORK_DIR = Path("obstacle_dataset_build")
OUTPUT_ZIP = Path("obstacle_dataset.zip")
CLASS_NAMES = ["person", "vehicle", "animal", "rock", "stump", "fence", "ditch"]
NUM_CLASSES = 7

# Images per class to download from free sources
IMAGES_PER_SEARCH = 30  # per search query
# Search queries for each class (diverse contexts)
SEARCH_QUERIES = {
    "rock": [
        "rock on dirt path", "boulder in grass field", "stones on farm road",
        "large rock outdoor", "rocks ground agriculture", "stone field path",
        "rock obstacle trail", "boulder meadow"
    ],
    "stump": [
        "tree stump in field", "cut tree stump grass", "tree stump farm",
        "old stump forest floor", "tree stump orchard", "wooden stump ground",
        "tree stump path", "stump removal field"
    ],
    "fence": [
        "farm fence rural field", "wooden fence pasture", "wire fence agriculture",
        "metal fence farm", "fence post field", "broken fence rural",
        "barbed wire fence paddock", "fence gate farm"
    ],
    "ditch": [
        "irrigation ditch farm", "drainage ditch field", "water channel agriculture",
        "trench farm road side", "ditch rural road", "dry irrigation canal",
        "farm drainage channel", "field ditch water"
    ],
}

# COCO class mapping
COCO_REMAP = {
    1: 0,   # person -> person
    3: 1, 6: 1, 8: 1, 4: 1,  # car/bus/truck/motorcycle -> vehicle
    17: 2, 18: 2, 19: 2, 20: 2, 21: 2, 16: 2,  # animals -> animal
}
MAX_COCO_PER_CLASS = 400

COCO_VAL_IMAGES_URL = "http://images.cocodataset.org/zips/val2017.zip"
COCO_VAL_ANN_URL = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"

TRAIN_RATIO = 0.80
VALID_RATIO = 0.10


# ============================================================================
# IMAGE DOWNLOADING (No API key needed - uses Unsplash source)
# ============================================================================

def download_images_unsplash(query: str, count: int, out_dir: Path) -> int:
    """Download images from Unsplash Source (no API key, random images)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    downloaded = 0
    query_clean = query.replace(" ", ",")

    for i in range(count):
        url = f"https://source.unsplash.com/640x480/?{query_clean}&sig={random.randint(1,99999)}"
        dest = out_dir / f"unsplash_{query_clean[:20]}_{i:03d}.jpg"
        if dest.exists():
            downloaded += 1
            continue
        try:
            urllib.request.urlretrieve(url, str(dest))
            # Check it's actually an image (not a redirect page)
            if dest.stat().st_size > 5000:
                downloaded += 1
            else:
                dest.unlink()
        except Exception:
            pass

    return downloaded


def download_images_for_class(class_name: str, queries: list, out_dir: Path) -> int:
    """Download images for a class using multiple search queries."""
    class_dir = out_dir / class_name
    class_dir.mkdir(parents=True, exist_ok=True)
    total = 0

    for query in queries:
        count = download_images_unsplash(query, IMAGES_PER_SEARCH, class_dir)
        total += count
        print(f"    '{query}': {count} images")

    print(f"  Total {class_name}: {total} images")
    return total


# ============================================================================
# AUTO-ANNOTATION WITH GROUNDING DINO
# ============================================================================

def auto_annotate_class(class_name: str, class_id: int,
                        images_dir: Path, output_dir: Path,
                        prompt: str, threshold: float = 0.25) -> int:
    """Use Grounding DINO to auto-annotate images for one class."""
    from autodistill_grounding_dino import GroundingDINO
    from autodistill.detection import CaptionOntology
    import supervision as sv
    from PIL import Image as PILImage

    # Define what Grounding DINO should look for
    ontology = CaptionOntology({prompt: class_name})
    model = GroundingDINO(ontology=ontology, box_threshold=threshold)

    img_out = output_dir / "images"
    lbl_out = output_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    images = sorted(p for p in images_dir.iterdir() if p.suffix.lower() in extensions)
    count = 0

    for img_path in tqdm(images, desc=f"  Annotating {class_name}"):
        try:
            # Get image dimensions
            with PILImage.open(img_path) as img:
                img_w, img_h = img.size

            # Run Grounding DINO
            result = model.predict(str(img_path))

            if result is None or len(result.xyxy) == 0:
                continue

            # Convert detections to YOLO format
            lines = []
            for box in result.xyxy:
                x1, y1, x2, y2 = box
                cx = ((x1 + x2) / 2) / img_w
                cy = ((y1 + y2) / 2) / img_h
                w = (x2 - x1) / img_w
                h = (y2 - y1) / img_h

                # Clamp
                cx = max(0.0, min(1.0, cx))
                cy = max(0.0, min(1.0, cy))
                w = max(0.001, min(1.0, w))
                h = max(0.001, min(1.0, h))

                lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

            if lines:
                stem = f"auto_{class_name}_{count:05d}"
                dst_img = img_out / f"{stem}{img_path.suffix}"
                dst_lbl = lbl_out / f"{stem}.txt"
                shutil.copy2(img_path, dst_img)
                dst_lbl.write_text("\n".join(lines) + "\n", encoding="utf-8")
                count += 1

        except Exception as e:
            continue

    print(f"  -> {count}/{len(images)} images auto-annotated for {class_name}")
    return count


# ============================================================================
# COCO PROCESSING (same as lite script)
# ============================================================================

def download(url: str, dest: Path):
    if dest.exists():
        print(f"  [exists] {dest.name}")
        return
    print(f"  Downloading {dest.name}...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest))
    print(f"  Done ({dest.stat().st_size / 1e6:.0f} MB)")


def extract(zip_path: Path, dest: Path):
    marker = dest / ".extracted"
    if marker.exists():
        return
    print(f"  Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    marker.touch()


def coco_to_yolo(bbox, img_w, img_h):
    x, y, w, h = bbox
    cx = min(1.0, max(0.0, (x + w / 2) / img_w))
    cy = min(1.0, max(0.0, (y + h / 2) / img_h))
    nw = min(1.0, max(0.001, w / img_w))
    nh = min(1.0, max(0.001, h / img_h))
    return cx, cy, nw, nh


def build_from_coco(merged_dir: Path):
    """Download COCO val2017 and extract person/vehicle/animal."""
    coco_dir = WORK_DIR / "coco_download"
    coco_dir.mkdir(parents=True, exist_ok=True)

    img_zip = coco_dir / "val2017.zip"
    ann_zip = coco_dir / "annotations.zip"
    download(COCO_VAL_IMAGES_URL, img_zip)
    download(COCO_VAL_ANN_URL, ann_zip)
    extract(img_zip, coco_dir)
    extract(ann_zip, coco_dir)

    # Find paths
    img_dir = None
    for candidate in coco_dir.rglob("val2017"):
        if candidate.is_dir():
            img_dir = candidate
            break
    if img_dir is None:
        img_dir = coco_dir / "val2017"

    ann_file = None
    for candidate in coco_dir.rglob("instances_val2017.json"):
        ann_file = candidate
        break
    if ann_file is None:
        print("ERROR: Cannot find COCO annotations!")
        return

    with open(ann_file) as f:
        coco = json.load(f)

    img_info = {img["id"]: img for img in coco["images"]}
    target_cats = set(COCO_REMAP.keys())

    img_anns = {}
    for ann in coco["annotations"]:
        if ann["category_id"] in target_cats and not ann.get("iscrowd", 0):
            img_anns.setdefault(ann["image_id"], []).append(ann)

    out_images = merged_dir / "images"
    out_labels = merged_dir / "labels"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    all_ids = list(img_anns.keys())
    random.shuffle(all_ids)

    class_counts = [0] * 3  # person, vehicle, animal
    copied = 0

    for img_id in tqdm(all_ids[:1500], desc="  COCO"):
        info = img_info.get(img_id)
        if info is None:
            continue
        src = img_dir / info["file_name"]
        if not src.exists():
            continue

        lines = []
        for ann in img_anns[img_id]:
            our_cls = COCO_REMAP.get(ann["category_id"])
            if our_cls is None:
                continue
            bbox = ann["bbox"]
            if bbox[2] <= 0 or bbox[3] <= 0:
                continue
            cx, cy, nw, nh = coco_to_yolo(bbox, info["width"], info["height"])
            lines.append(f"{our_cls} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
            class_counts[our_cls] += 1

        if lines:
            stem = f"coco_{img_id:012d}"
            shutil.copy2(src, out_images / f"{stem}{src.suffix}")
            (out_labels / f"{stem}.txt").write_text(
                "\n".join(lines) + "\n", encoding="utf-8")
            copied += 1

    print(f"  COCO: {copied} images")
    print(f"    person: {class_counts[0]} objects")
    print(f"    vehicle: {class_counts[1]} objects")
    print(f"    animal: {class_counts[2]} objects")


# ============================================================================
# SPLIT AND PACKAGE
# ============================================================================

def split_and_package(merged_dir: Path):
    final_dir = WORK_DIR / "final"
    if final_dir.exists():
        shutil.rmtree(final_dir)

    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    img_dir = merged_dir / "images"
    lbl_dir = merged_dir / "labels"

    pairs = []
    for img in sorted(img_dir.iterdir()):
        if img.suffix.lower() in extensions:
            lbl = lbl_dir / f"{img.stem}.txt"
            if lbl.exists():
                pairs.append((img, lbl))

    random.shuffle(pairs)
    n = len(pairs)
    t_end = int(TRAIN_RATIO * n)
    v_end = t_end + int(VALID_RATIO * n)
    splits = {"train": pairs[:t_end], "valid": pairs[t_end:v_end], "test": pairs[v_end:]}

    for name, items in splits.items():
        (final_dir / name / "images").mkdir(parents=True, exist_ok=True)
        (final_dir / name / "labels").mkdir(parents=True, exist_ok=True)
        for img, lbl in items:
            shutil.copy2(img, final_dir / name / "images" / img.name)
            shutil.copy2(lbl, final_dir / name / "labels" / lbl.name)
        print(f"    {name}: {len(items)}")

    # dataset.yaml
    cfg = {"path": ".", "train": "train/images", "val": "valid/images",
           "test": "test/images", "nc": NUM_CLASSES, "names": CLASS_NAMES}
    (final_dir / "dataset.yaml").write_text(
        yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")

    # Validate
    class_counts = [0] * NUM_CLASSES
    for split in ("train", "valid", "test"):
        for lbl in (final_dir / split / "labels").glob("*.txt"):
            for line in lbl.read_text().splitlines():
                parts = line.split()
                if len(parts) == 5:
                    cid = int(parts[0])
                    if 0 <= cid < NUM_CLASSES:
                        class_counts[cid] += 1

    print(f"\n  Final counts: {dict(zip(CLASS_NAMES, class_counts))}")
    missing = [CLASS_NAMES[i] for i, c in enumerate(class_counts) if c == 0]
    if missing:
        print(f"  *** WARNING: Zero annotations for: {missing} ***")
        return False

    # ZIP
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(final_dir.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(final_dir))
    print(f"\n  ✓ {OUTPUT_ZIP} ({OUTPUT_ZIP.stat().st_size / 1e6:.1f} MB)")
    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("FULLY AUTOMATED Obstacle Dataset Builder")
    print("(Grounding DINO auto-annotation + COCO + Unsplash)")
    print("=" * 70)

    merged_dir = WORK_DIR / "merged"
    if merged_dir.exists():
        shutil.rmtree(merged_dir)
    merged_dir.mkdir(parents=True, exist_ok=True)

    # ---- Step 1: COCO for person/vehicle/animal ----
    print("\n[1/4] COCO 2017 val -> person, vehicle, animal")
    print("-" * 50)
    build_from_coco(merged_dir)

    # ---- Step 2: Download images for rare classes ----
    print("\n[2/4] Downloading images for rock/stump/fence/ditch")
    print("-" * 50)
    raw_dir = WORK_DIR / "raw_images"
    for class_name, queries in SEARCH_QUERIES.items():
        print(f"\n  [{class_name}]")
        download_images_for_class(class_name, queries, raw_dir)

    # ---- Step 3: Auto-annotate with Grounding DINO ----
    print("\n[3/4] Auto-annotating with Grounding DINO (zero-shot)")
    print("-" * 50)

    # Prompts tuned for Grounding DINO (what to detect in each image)
    prompts = {
        "rock": ("rock . boulder . stone on ground", 3, 0.25),
        "stump": ("tree stump . cut tree stump . wooden stump", 4, 0.25),
        "fence": ("fence . wire fence . wooden fence . metal fence", 5, 0.20),
        "ditch": ("ditch . trench . canal . drainage channel . irrigation channel", 6, 0.20),
    }

    for class_name, (prompt, class_id, threshold) in prompts.items():
        src_dir = raw_dir / class_name
        if not src_dir.exists() or not any(src_dir.iterdir()):
            print(f"  [skip] No images for {class_name}")
            continue
        auto_annotate_class(class_name, class_id, src_dir, merged_dir,
                           prompt, threshold)

    # ---- Step 4: Split and package ----
    print("\n[4/4] Splitting and packaging")
    print("-" * 50)
    ok = split_and_package(merged_dir)

    if ok:
        print("\n" + "=" * 70)
        print("✓ SUCCESS! Upload obstacle_dataset.zip to Colab notebook.")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("Dataset incomplete. Check warnings above.")
        print("=" * 70)


if __name__ == "__main__":
    main()
