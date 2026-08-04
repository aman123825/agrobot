"""
AgriRover Obstacle Dataset Preparation Script
=============================================
Downloads images from COCO 2017 and Open Images V7 for the 7 obstacle classes,
remaps them to the required class IDs, and packages everything into the ZIP
format expected by training/obstacle_detection.ipynb.

Required classes (in order):
  0: person
  1: vehicle  (car, truck, bus from COCO)
  2: animal   (cow, sheep, horse, dog, cat from COCO)
  3: rock     (manual collection required - see instructions below)
  4: stump    (manual collection required)
  5: fence    (Open Images V7)
  6: ditch    (manual collection required)

Usage:
  pip install pycocotools fiftyone Pillow tqdm pyyaml
  python prepare_obstacle_dataset.py

The script will:
  1. Download COCO 2017 val+train subsets for person/vehicle/animal
  2. Download Open Images V7 subset for fence
  3. Merge everything into a unified YOLO dataset
  4. Create an 80/10/10 train/valid/test split
  5. Package as obstacle_dataset.zip ready for Colab upload

For rock/stump/ditch: add your own annotated images to the manual_data/
folder BEFORE running this script. See MANUAL DATA section below.

Author: AgriRover team
"""

import hashlib
import json
import os
import random
import shutil
import zipfile
from pathlib import Path
from typing import Optional

import yaml

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

# ============================================================================
# CONFIGURATION
# ============================================================================

SEED = 42
random.seed(SEED)

# Output paths
WORK_DIR = Path("obstacle_dataset_build")
OUTPUT_ZIP = Path("obstacle_dataset.zip")

# Target class mapping
CLASS_NAMES = ["person", "vehicle", "animal", "rock", "stump", "fence", "ditch"]
NUM_CLASSES = len(CLASS_NAMES)

# How many images to sample per source class (keeps dataset balanced)
# Increase these if you want more data (but download will take longer)
MAX_IMAGES_PER_CLASS = 400  # per source class from COCO/OI
MAX_IMAGES_COCO_PERSON = 500
MAX_IMAGES_COCO_VEHICLE = 400  # across car+truck+bus
MAX_IMAGES_COCO_ANIMAL = 400   # across cow+sheep+horse+dog+cat
MAX_IMAGES_OI_FENCE = 300

# COCO 2017 class IDs -> our class IDs
COCO_PERSON_ID = 1        # -> 0 (person)
COCO_VEHICLE_IDS = {3: "car", 6: "bus", 8: "truck"}  # -> 1 (vehicle)
COCO_ANIMAL_IDS = {16: "bird", 17: "cat", 18: "dog",
                   19: "horse", 20: "sheep", 21: "cow"}  # -> 2 (animal)

# Split ratios
TRAIN_RATIO = 0.80
VALID_RATIO = 0.10
TEST_RATIO = 0.10

# Manual data folder (for rock, stump, fence supplement, ditch)
MANUAL_DATA_DIR = Path("manual_data")



# ============================================================================
# COCO 2017 DOWNLOAD AND FILTERING
# ============================================================================

COCO_URLS = {
    "train_images": "http://images.cocodataset.org/zips/train2017.zip",
    "val_images": "http://images.cocodataset.org/zips/val2017.zip",
    "annotations": "http://images.cocodataset.org/annotations/annotations_trainval2017.zip",
}


def download_file(url: str, dest: Path, chunk_size: int = 8192) -> Path:
    """Download a file with progress bar. Skips if already exists."""
    if dest.exists():
        print(f"  [skip] {dest.name} already exists")
        return dest
    import urllib.request
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading {dest.name} ...")
    urllib.request.urlretrieve(url, str(dest))
    print(f"  Done: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
    return dest


def extract_zip(zip_path: Path, dest_dir: Path):
    """Extract a ZIP file if not already extracted."""
    if dest_dir.exists() and any(dest_dir.iterdir()):
        print(f"  [skip] {dest_dir.name} already extracted")
        return
    print(f"  Extracting {zip_path.name} ...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    print(f"  Extracted to {dest_dir}")


def load_coco_annotations(ann_file: Path) -> dict:
    """Load COCO JSON annotations."""
    print(f"  Loading {ann_file.name} ...")
    with open(ann_file, "r") as f:
        return json.load(f)


def filter_coco_images(coco_data: dict, target_cat_ids: set,
                       max_images: int) -> list[dict]:
    """Get images that contain at least one annotation with target categories."""
    # Build image_id -> annotations mapping
    img_anns = {}
    for ann in coco_data["annotations"]:
        if ann["category_id"] in target_cat_ids:
            img_id = ann["image_id"]
            if img_id not in img_anns:
                img_anns[img_id] = []
            img_anns[img_id].append(ann)

    # Get image info for those images
    img_lookup = {img["id"]: img for img in coco_data["images"]}
    selected = []
    for img_id in list(img_anns.keys())[:max_images]:
        if img_id in img_lookup:
            selected.append({
                "image_info": img_lookup[img_id],
                "annotations": img_anns[img_id],
            })
    random.shuffle(selected)
    return selected[:max_images]


def coco_bbox_to_yolo(bbox: list, img_w: int, img_h: int) -> tuple:
    """Convert COCO bbox [x,y,w,h] (pixels) to YOLO [cx,cy,w,h] (normalized)."""
    x, y, w, h = bbox
    cx = (x + w / 2.0) / img_w
    cy = (y + h / 2.0) / img_h
    nw = w / img_w
    nh = h / img_h
    # Clamp to [0, 1]
    cx = max(0.0, min(1.0, cx))
    cy = max(0.0, min(1.0, cy))
    nw = max(0.001, min(1.0, nw))
    nh = max(0.001, min(1.0, nh))
    return (cx, cy, nw, nh)


def process_coco_for_class(coco_data: dict, coco_cat_ids: set,
                           our_class_id: int, images_dir: Path,
                           output_dir: Path, max_images: int,
                           class_name: str) -> int:
    """Filter COCO images for given categories, convert to YOLO format."""
    print(f"\n  Processing COCO -> {class_name} (class {our_class_id})...")
    filtered = filter_coco_images(coco_data, coco_cat_ids, max_images)
    count = 0

    img_out = output_dir / "images"
    lbl_out = output_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    for item in tqdm(filtered, desc=f"  {class_name}"):
        img_info = item["image_info"]
        file_name = img_info["file_name"]
        img_w = img_info["width"]
        img_h = img_info["height"]

        src_path = images_dir / file_name
        if not src_path.exists():
            continue

        # Generate unique name to avoid collisions
        stem = f"coco_{class_name}_{img_info['id']:012d}"
        suffix = src_path.suffix
        dst_img = img_out / f"{stem}{suffix}"
        dst_lbl = lbl_out / f"{stem}.txt"

        # Copy image
        shutil.copy2(src_path, dst_img)

        # Write YOLO labels (only for our target categories)
        lines = []
        for ann in item["annotations"]:
            if ann["category_id"] in coco_cat_ids:
                if ann.get("iscrowd", 0):
                    continue
                bbox = ann["bbox"]
                if bbox[2] <= 0 or bbox[3] <= 0:
                    continue
                cx, cy, nw, nh = coco_bbox_to_yolo(bbox, img_w, img_h)
                lines.append(f"{our_class_id} {cx:.6f} {cy:.6f} {nw:.6f} {nh:.6f}")

        if lines:
            dst_lbl.write_text("\n".join(lines) + "\n", encoding="utf-8")
            count += 1
        else:
            dst_img.unlink(missing_ok=True)

    print(f"  -> {count} images with {class_name} annotations")
    return count



# ============================================================================
# OPEN IMAGES V7 - FENCE CLASS
# ============================================================================

def download_open_images_fence(output_dir: Path, max_images: int) -> int:
    """Download fence images from Open Images V7 using FiftyOne."""
    print(f"\n  Downloading Open Images V7 -> fence (class 5)...")
    try:
        import fiftyone as fo
        import fiftyone.zoo as foz
    except ImportError:
        print("  [ERROR] fiftyone not installed. Install with: pip install fiftyone")
        print("  Skipping Open Images fence download.")
        print("  You can manually add fence images to manual_data/fence/ instead.")
        return 0

    img_out = output_dir / "images"
    lbl_out = output_dir / "labels"
    img_out.mkdir(parents=True, exist_ok=True)
    lbl_out.mkdir(parents=True, exist_ok=True)

    # Download fence class from Open Images
    dataset = foz.load_zoo_dataset(
        "open-images-v7",
        split="train",
        label_types=["detections"],
        classes=["Fence"],
        max_samples=max_images,
        dataset_name="oi7_fence_temp",
    )

    count = 0
    for sample in dataset:
        if sample.filepath is None or not os.path.exists(sample.filepath):
            continue

        detections = sample.ground_truth
        if detections is None:
            continue

        # Filter only Fence detections
        fence_dets = [d for d in detections.detections if d.label == "Fence"]
        if not fence_dets:
            continue

        # Get image dimensions
        from PIL import Image as PILImage
        try:
            with PILImage.open(sample.filepath) as img:
                img_w, img_h = img.size
        except Exception:
            continue

        stem = f"oi7_fence_{count:06d}"
        suffix = Path(sample.filepath).suffix
        dst_img = img_out / f"{stem}{suffix}"
        dst_lbl = lbl_out / f"{stem}.txt"

        shutil.copy2(sample.filepath, dst_img)

        lines = []
        for det in fence_dets:
            # FiftyOne bbox is [x, y, w, h] normalized
            x, y, w, h = det.bounding_box
            cx = x + w / 2.0
            cy = y + h / 2.0
            cx = max(0.0, min(1.0, cx))
            cy = max(0.0, min(1.0, cy))
            w = max(0.001, min(1.0, w))
            h = max(0.001, min(1.0, h))
            lines.append(f"5 {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

        if lines:
            dst_lbl.write_text("\n".join(lines) + "\n", encoding="utf-8")
            count += 1
        else:
            dst_img.unlink(missing_ok=True)

    # Cleanup FiftyOne dataset
    try:
        fo.delete_dataset("oi7_fence_temp")
    except Exception:
        pass

    print(f"  -> {count} images with fence annotations")
    return count


# ============================================================================
# MANUAL DATA INTEGRATION (rock, stump, ditch, extra fence)
# ============================================================================

def integrate_manual_data(output_dir: Path) -> dict[str, int]:
    """
    Copy manually annotated images from manual_data/ into the build directory.

    Expected structure:
      manual_data/
        rock/
          images/   (*.jpg, *.png)
          labels/   (*.txt in YOLO format, class_id MUST be 3)
        stump/
          images/
          labels/   (class_id MUST be 4)
        fence/
          images/
          labels/   (class_id MUST be 5)
        ditch/
          images/
          labels/   (class_id MUST be 6)

    Each .txt label file uses standard YOLO format:
      <class_id> <x_center> <y_center> <width> <height>
    All coordinates normalized 0..1.
    """
    counts = {}
    class_map = {"rock": 3, "stump": 4, "fence": 5, "ditch": 6}

    for class_name, class_id in class_map.items():
        src_dir = MANUAL_DATA_DIR / class_name
        if not src_dir.exists():
            print(f"  [skip] manual_data/{class_name}/ not found")
            counts[class_name] = 0
            continue

        src_images = src_dir / "images"
        src_labels = src_dir / "labels"
        if not src_images.exists() or not src_labels.exists():
            print(f"  [skip] manual_data/{class_name}/images/ or labels/ missing")
            counts[class_name] = 0
            continue

        img_out = output_dir / "images"
        lbl_out = output_dir / "labels"
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)

        count = 0
        extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        for img_path in sorted(src_images.iterdir()):
            if img_path.suffix.lower() not in extensions:
                continue
            lbl_path = src_labels / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                print(f"    [warn] No label for {img_path.name}")
                continue

            stem = f"manual_{class_name}_{count:06d}"
            dst_img = img_out / f"{stem}{img_path.suffix}"
            dst_lbl = lbl_out / f"{stem}.txt"

            shutil.copy2(img_path, dst_img)
            shutil.copy2(lbl_path, dst_lbl)
            count += 1

        print(f"  manual_data/{class_name}: {count} images")
        counts[class_name] = count

    return counts



# ============================================================================
# DATASET SPLITTING AND PACKAGING
# ============================================================================

def split_dataset(merged_dir: Path, final_dir: Path):
    """Split merged images/labels into train/valid/test (80/10/10)."""
    print("\n  Splitting dataset into train/valid/test...")

    img_dir = merged_dir / "images"
    lbl_dir = merged_dir / "labels"

    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    all_images = sorted(
        p for p in img_dir.iterdir() if p.suffix.lower() in extensions
    )

    # Only keep images that have a corresponding label
    pairs = []
    for img_path in all_images:
        lbl_path = lbl_dir / f"{img_path.stem}.txt"
        if lbl_path.exists():
            pairs.append((img_path, lbl_path))

    print(f"  Total image/label pairs: {len(pairs)}")
    random.shuffle(pairs)

    n = len(pairs)
    train_end = int(TRAIN_RATIO * n)
    valid_end = train_end + int(VALID_RATIO * n)

    splits = {
        "train": pairs[:train_end],
        "valid": pairs[train_end:valid_end],
        "test": pairs[valid_end:],
    }

    for split_name, split_pairs in splits.items():
        split_img_dir = final_dir / split_name / "images"
        split_lbl_dir = final_dir / split_name / "labels"
        split_img_dir.mkdir(parents=True, exist_ok=True)
        split_lbl_dir.mkdir(parents=True, exist_ok=True)

        for img_path, lbl_path in split_pairs:
            shutil.copy2(img_path, split_img_dir / img_path.name)
            shutil.copy2(lbl_path, split_lbl_dir / lbl_path.name)

        print(f"  {split_name}: {len(split_pairs)} images")

    return splits


def write_dataset_yaml(final_dir: Path):
    """Write the dataset.yaml file required by the notebook."""
    config = {
        "path": ".",
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": NUM_CLASSES,
        "names": CLASS_NAMES,
    }
    yaml_path = final_dir / "dataset.yaml"
    yaml_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    print(f"\n  Written: {yaml_path}")
    print(f"  Contents:\n{yaml_path.read_text()}")


def validate_dataset(final_dir: Path) -> bool:
    """Quick validation matching the notebook's checks."""
    print("\n  Validating dataset...")
    errors = []
    class_counts = [0] * NUM_CLASSES
    extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for split in ("train", "valid", "test"):
        img_dir = final_dir / split / "images"
        lbl_dir = final_dir / split / "labels"
        if not img_dir.exists() or not lbl_dir.exists():
            errors.append(f"Missing {split}/images or {split}/labels")
            continue

        images = [p for p in img_dir.iterdir() if p.suffix.lower() in extensions]
        for img_path in images:
            lbl_path = lbl_dir / f"{img_path.stem}.txt"
            if not lbl_path.exists():
                errors.append(f"Missing label: {lbl_path.name}")
                continue
            for line in lbl_path.read_text().splitlines():
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) != 5:
                    errors.append(f"{lbl_path.name}: bad line (not 5 values)")
                    continue
                try:
                    cid = int(parts[0])
                    coords = [float(v) for v in parts[1:]]
                except ValueError:
                    errors.append(f"{lbl_path.name}: non-numeric value")
                    continue
                if not (0 <= cid < NUM_CLASSES):
                    errors.append(f"{lbl_path.name}: class {cid} out of range")
                elif all(0 <= v <= 1 for v in coords) and coords[2] > 0 and coords[3] > 0:
                    class_counts[cid] += 1

    missing_classes = [CLASS_NAMES[i] for i, c in enumerate(class_counts) if c == 0]
    if missing_classes:
        errors.append(f"Classes with ZERO annotations: {missing_classes}")

    print(f"  Objects per class: {dict(zip(CLASS_NAMES, class_counts))}")
    if errors:
        print(f"\n  *** VALIDATION ERRORS ({len(errors)}) ***")
        for e in errors[:20]:
            print(f"    - {e}")
        return False
    else:
        print("  ✓ Dataset validation PASSED")
        return True


def create_zip(final_dir: Path, zip_path: Path):
    """Package the final dataset into a ZIP for Colab upload."""
    print(f"\n  Creating {zip_path.name}...")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(final_dir.rglob("*")):
            if file_path.is_file():
                arcname = file_path.relative_to(final_dir)
                zf.write(file_path, arcname)
    size_mb = zip_path.stat().st_size / 1e6
    print(f"  ✓ Created: {zip_path} ({size_mb:.1f} MB)")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("AgriRover Obstacle Dataset Preparation")
    print("=" * 70)
    print(f"\nTarget classes: {CLASS_NAMES}")
    print(f"Work directory: {WORK_DIR}")
    print(f"Output ZIP:     {OUTPUT_ZIP}")

    # Create work directories
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    merged_dir = WORK_DIR / "merged"
    final_dir = WORK_DIR / "final"

    if merged_dir.exists():
        shutil.rmtree(merged_dir)
    if final_dir.exists():
        shutil.rmtree(final_dir)
    merged_dir.mkdir(parents=True)
    final_dir.mkdir(parents=True)

    # ---- Step 1: Download COCO 2017 ----
    print("\n" + "=" * 70)
    print("STEP 1: COCO 2017 - person, vehicle, animal")
    print("=" * 70)

    coco_dir = WORK_DIR / "coco"
    coco_dir.mkdir(parents=True, exist_ok=True)

    # Download annotations (smaller, ~250 MB)
    ann_zip = download_file(
        COCO_URLS["annotations"],
        coco_dir / "annotations_trainval2017.zip"
    )
    extract_zip(ann_zip, coco_dir)

    # Download val images first (smaller: 1 GB vs 18 GB for train)
    # For a prototype dataset, val2017 (5000 images) is often sufficient
    val_zip = download_file(
        COCO_URLS["val_images"],
        coco_dir / "val2017.zip"
    )
    extract_zip(val_zip, coco_dir)

    # Load annotations
    ann_file = coco_dir / "annotations" / "instances_val2017.json"
    if not ann_file.exists():
        # Try alternate extraction path
        ann_file = coco_dir / "annotations_trainval2017" / "annotations" / "instances_val2017.json"
    if not ann_file.exists():
        # Search for it
        candidates = list(coco_dir.rglob("instances_val2017.json"))
        if candidates:
            ann_file = candidates[0]
        else:
            print("ERROR: Could not find instances_val2017.json!")
            print("Download COCO 2017 annotations manually from:")
            print("  http://images.cocodataset.org/annotations/annotations_trainval2017.zip")
            return

    coco_data = load_coco_annotations(ann_file)

    # Find COCO images directory
    val_img_dir = coco_dir / "val2017"
    if not val_img_dir.exists():
        candidates = list(coco_dir.rglob("val2017"))
        val_img_dir = candidates[0] if candidates else coco_dir

    # Process person
    process_coco_for_class(
        coco_data, {COCO_PERSON_ID}, 0,
        val_img_dir, merged_dir, MAX_IMAGES_COCO_PERSON, "person"
    )

    # Process vehicle (car=3, bus=6, truck=8)
    process_coco_for_class(
        coco_data, set(COCO_VEHICLE_IDS.keys()), 1,
        val_img_dir, merged_dir, MAX_IMAGES_COCO_VEHICLE, "vehicle"
    )

    # Process animal (cat=17, dog=18, horse=19, sheep=20, cow=21)
    process_coco_for_class(
        coco_data, set(COCO_ANIMAL_IDS.keys()), 2,
        val_img_dir, merged_dir, MAX_IMAGES_COCO_ANIMAL, "animal"
    )

    # ---- Step 2: Open Images V7 - Fence ----
    print("\n" + "=" * 70)
    print("STEP 2: Open Images V7 - fence")
    print("=" * 70)
    download_open_images_fence(merged_dir, MAX_IMAGES_OI_FENCE)

    # ---- Step 3: Manual data (rock, stump, ditch) ----
    print("\n" + "=" * 70)
    print("STEP 3: Manual data - rock, stump, fence (extra), ditch")
    print("=" * 70)
    manual_counts = integrate_manual_data(merged_dir)

    # ---- Step 4: Split ----
    print("\n" + "=" * 70)
    print("STEP 4: Train/Valid/Test split (80/10/10)")
    print("=" * 70)
    split_dataset(merged_dir, final_dir)

    # ---- Step 5: Write YAML ----
    write_dataset_yaml(final_dir)

    # ---- Step 6: Validate ----
    print("\n" + "=" * 70)
    print("STEP 5: Validation")
    print("=" * 70)
    valid = validate_dataset(final_dir)

    if not valid:
        print("\n*** WARNING: Dataset has issues! ***")
        print("The notebook will likely reject it. Fix the errors above.")
        print("Most common fix: add manual images for rock/stump/ditch.")
    else:
        # ---- Step 7: Package ZIP ----
        print("\n" + "=" * 70)
        print("STEP 6: Packaging ZIP")
        print("=" * 70)
        create_zip(final_dir, OUTPUT_ZIP)

        print("\n" + "=" * 70)
        print("DONE!")
        print("=" * 70)
        print(f"\n  Upload {OUTPUT_ZIP} to the obstacle_detection.ipynb notebook.")
        print("  The notebook validates class order and annotations before training.")


if __name__ == "__main__":
    main()
