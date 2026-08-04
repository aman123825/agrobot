"""
Lightweight Obstacle Dataset Builder (NO FiftyOne required)
===========================================================
Uses only pycocotools + urllib to build the dataset from COCO 2017 val.
Fence images must come from manual_data/fence/ (or use the full script
with FiftyOne for Open Images).

Usage:
  pip install pycocotools Pillow tqdm pyyaml
  python prepare_obstacle_dataset_lite.py

This is faster and lighter than prepare_obstacle_dataset.py but requires
you to manually provide fence images (in addition to rock/stump/ditch).
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
MANUAL_DATA_DIR = Path("manual_data")

CLASS_NAMES = ["person", "vehicle", "animal", "rock", "stump", "fence", "ditch"]
NUM_CLASSES = 7

# COCO category_id -> our class_id
COCO_REMAP = {
    1: 0,    # person -> person
    3: 1,    # car -> vehicle
    6: 1,    # bus -> vehicle
    8: 1,    # truck -> vehicle
    4: 1,    # motorcycle -> vehicle
    17: 2,   # cat -> animal
    18: 2,   # dog -> animal
    19: 2,   # horse -> animal
    20: 2,   # sheep -> animal
    21: 2,   # cow -> animal
    16: 2,   # bird -> animal
}

# Max images to use per our-class from COCO
MAX_PER_CLASS = {"person": 500, "vehicle": 400, "animal": 400}

COCO_VAL_IMAGES_URL = "http://images.cocodataset.org/zips/val2017.zip"
COCO_VAL_ANN_URL = "http://images.cocodataset.org/annotations/annotations_trainval2017.zip"

TRAIN_RATIO = 0.80
VALID_RATIO = 0.10


# ============================================================================
# HELPERS
# ============================================================================

def download(url: str, dest: Path):
    if dest.exists():
        print(f"  [exists] {dest.name}")
        return
    print(f"  Downloading {dest.name} ({url.split('/')[-1]})...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, str(dest))
    print(f"  Done ({dest.stat().st_size / 1e6:.0f} MB)")


def extract(zip_path: Path, dest: Path):
    marker = dest / ".extracted"
    if marker.exists():
        print(f"  [extracted] {dest.name}")
        return
    print(f"  Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
    marker.touch()


def coco_to_yolo(bbox, img_w, img_h):
    """COCO [x,y,w,h] pixels -> YOLO [cx,cy,w,h] normalized."""
    x, y, w, h = bbox
    cx = min(1.0, max(0.0, (x + w / 2) / img_w))
    cy = min(1.0, max(0.0, (y + h / 2) / img_h))
    nw = min(1.0, max(0.001, w / img_w))
    nh = min(1.0, max(0.001, h / img_h))
    return cx, cy, nw, nh


# ============================================================================
# MAIN BUILD
# ============================================================================

def build_from_coco():
    """Download COCO val2017 and extract person/vehicle/animal."""
    coco_dir = WORK_DIR / "coco_download"
    coco_dir.mkdir(parents=True, exist_ok=True)

    # Download
    img_zip = coco_dir / "val2017.zip"
    ann_zip = coco_dir / "annotations.zip"
    download(COCO_VAL_IMAGES_URL, img_zip)
    download(COCO_VAL_ANN_URL, ann_zip)

    # Extract
    extract(img_zip, coco_dir)
    extract(ann_zip, coco_dir)

    # Find paths
    img_dir = None
    for candidate in [coco_dir / "val2017", coco_dir]:
        if (candidate / "000000000139.jpg").exists() or list(candidate.glob("*.jpg")):
            img_dir = candidate
            break
    if img_dir is None:
        # Search
        jpgs = list(coco_dir.rglob("000000000139.jpg"))
        img_dir = jpgs[0].parent if jpgs else coco_dir / "val2017"

    ann_file = None
    for candidate in coco_dir.rglob("instances_val2017.json"):
        ann_file = candidate
        break
    if ann_file is None:
        print("ERROR: Cannot find instances_val2017.json")
        return {}

    print(f"  Images: {img_dir}")
    print(f"  Annotations: {ann_file}")

    # Load annotations
    with open(ann_file) as f:
        coco = json.load(f)

    # Index: image_id -> image info
    img_info = {img["id"]: img for img in coco["images"]}

    # Group annotations by image, keeping only our target categories
    target_cats = set(COCO_REMAP.keys())
    img_anns = {}
    for ann in coco["annotations"]:
        if ann["category_id"] in target_cats and not ann.get("iscrowd", 0):
            iid = ann["image_id"]
            img_anns.setdefault(iid, []).append(ann)

    # For each of our classes, collect images
    # An image can contribute to multiple classes (person + vehicle in same frame)
    merged_dir = WORK_DIR / "merged"
    out_images = merged_dir / "images"
    out_labels = merged_dir / "labels"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    # Track which images we've already copied (avoid duplicates)
    copied_images = set()
    class_obj_counts = [0] * NUM_CLASSES

    # Shuffle image IDs for randomness
    all_img_ids = list(img_anns.keys())
    random.shuffle(all_img_ids)

    # Count how many images primarily contribute to each class
    class_img_counts = {"person": 0, "vehicle": 0, "animal": 0}

    for img_id in tqdm(all_img_ids, desc="  COCO processing"):
        info = img_info.get(img_id)
        if info is None:
            continue

        anns = img_anns[img_id]
        img_w, img_h = info["width"], info["height"]
        file_name = info["file_name"]
        src = img_dir / file_name

        if not src.exists():
            continue

        # Determine which of our classes are in this image
        our_classes_present = set()
        for ann in anns:
            our_cls = COCO_REMAP.get(ann["category_id"])
            if our_cls is not None:
                our_classes_present.add(our_cls)

        # Check if we still need images for any present class
        need = False
        for cls_id in our_classes_present:
            cls_name = CLASS_NAMES[cls_id]
            limit = MAX_PER_CLASS.get(cls_name, 999)
            if class_img_counts.get(cls_name, 0) < limit:
                need = True
                break

        if not need:
            continue

        # Copy image and write labels
        stem = f"coco_{img_id:012d}"
        dst_img = out_images / f"{stem}{src.suffix}"
        dst_lbl = out_labels / f"{stem}.txt"

        if img_id not in copied_images:
            shutil.copy2(src, dst_img)
            copied_images.add(img_id)

        lines = []
        for ann in anns:
            our_cls = COCO_REMAP.get(ann["category_id"])
            if our_cls is None:
                continue
            bbox = ann["bbox"]
            if bbox[2] <= 0 or bbox[3] <= 0:
                continue
            cx, cy, nw, nh = coco_to_yolo(bbox, img_w, img_h)
            lines.append(f"{our_cls} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")
            class_obj_counts[our_cls] += 1

        if lines:
            dst_lbl.write_text("\n".join(lines) + "\n", encoding="utf-8")
            for cls_id in our_classes_present:
                cls_name = CLASS_NAMES[cls_id]
                class_img_counts[cls_name] = class_img_counts.get(cls_name, 0) + 1

    print(f"\n  COCO results:")
    print(f"    Images copied: {len(copied_images)}")
    print(f"    Objects: {dict(zip(CLASS_NAMES[:3], class_obj_counts[:3]))}")
    return class_obj_counts


def integrate_manual():
    """Copy manual images for rock/stump/fence/ditch."""
    print("\n  Integrating manual data...")
    merged_dir = WORK_DIR / "merged"
    out_images = merged_dir / "images"
    out_labels = merged_dir / "labels"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    counts = {}

    for class_name in ["rock", "stump", "fence", "ditch"]:
        src = MANUAL_DATA_DIR / class_name
        src_img = src / "images"
        src_lbl = src / "labels"

        if not src_img.exists() or not src_lbl.exists():
            print(f"    {class_name}: NOT FOUND (add to manual_data/{class_name}/)")
            counts[class_name] = 0
            continue

        count = 0
        for img_path in sorted(src_img.iterdir()):
            if img_path.suffix.lower() not in extensions:
                continue
            lbl_path = src_lbl / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                continue

            stem = f"manual_{class_name}_{count:05d}"
            shutil.copy2(img_path, out_images / f"{stem}{img_path.suffix}")
            shutil.copy2(lbl_path, out_labels / f"{stem}.txt")
            count += 1

        print(f"    {class_name}: {count} images")
        counts[class_name] = count

    return counts


def split_and_package():
    """Split into train/valid/test and create ZIP."""
    merged_dir = WORK_DIR / "merged"
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

    # Write dataset.yaml
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

    print(f"\n  Final object counts: {dict(zip(CLASS_NAMES, class_counts))}")
    missing = [CLASS_NAMES[i] for i, c in enumerate(class_counts) if c == 0]
    if missing:
        print(f"\n  *** WARNING: Zero annotations for: {missing} ***")
        print("  Add images to manual_data/ for these classes and re-run.")
        print("  The Colab notebook will REJECT this dataset.")
        return False

    # Create ZIP
    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()
    print(f"\n  Creating {OUTPUT_ZIP}...")
    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(final_dir.rglob("*")):
            if f.is_file():
                zf.write(f, f.relative_to(final_dir))
    print(f"  ✓ {OUTPUT_ZIP} ({OUTPUT_ZIP.stat().st_size / 1e6:.1f} MB)")
    return True


def main():
    print("=" * 60)
    print("AgriRover Obstacle Dataset Builder (Lite)")
    print("=" * 60)

    # Clean merged dir
    merged = WORK_DIR / "merged"
    if merged.exists():
        shutil.rmtree(merged)

    # Step 1: COCO
    print("\n[1/3] Downloading COCO 2017 val (person/vehicle/animal)...")
    build_from_coco()

    # Step 2: Manual data
    print("\n[2/3] Integrating manual data (rock/stump/fence/ditch)...")
    integrate_manual()

    # Step 3: Split + ZIP
    print("\n[3/3] Splitting and packaging...")
    ok = split_and_package()

    if ok:
        print("\n" + "=" * 60)
        print("SUCCESS! Upload obstacle_dataset.zip to Colab.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("INCOMPLETE - add manual data and re-run.")
        print("=" * 60)


if __name__ == "__main__":
    main()
