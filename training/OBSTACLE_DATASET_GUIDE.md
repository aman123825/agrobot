# Obstacle Detection Dataset - Complete Guide

## Overview

The `obstacle_detection.ipynb` notebook needs a 7-class YOLO dataset packaged
as `obstacle_dataset.zip`. This guide explains how to build it from scratch.

**Required classes (in exact order):**

| ID | Class   | Source                                  |
|----|---------|----------------------------------------|
| 0  | person  | COCO 2017 (automatic)                  |
| 1  | vehicle | COCO 2017 - car/truck/bus (automatic)  |
| 2  | animal  | COCO 2017 - cow/sheep/horse/dog/cat (automatic) |
| 3  | rock    | **Manual field photography + annotation** |
| 4  | stump   | **Manual field photography + annotation** |
| 5  | fence   | Open Images V7 + manual supplement     |
| 6  | ditch   | **Manual field photography + annotation** |

---

## Quick Start (Fastest Path)

### Option A: Automated script (recommended)

```bash
cd training/
pip install pycocotools fiftyone Pillow tqdm pyyaml
python prepare_obstacle_dataset.py
```

This downloads COCO + Open Images for person/vehicle/animal/fence automatically.
You still need to add rock/stump/ditch manually (see below).

### Option B: Skip the script, do it all manually

Use the annotation tool instructions below for all 7 classes.

---

## Step 1: Collect Images for Rock, Stump, Ditch

These classes are NOT available in any major public dataset. You must
photograph them yourself (best) or scrape from image search (less ideal).

### What to photograph

**Rock (class 3)** — target: 100-300 images
- Rocks on farm paths, field edges, between rows
- Sizes: fist-sized to boulder-sized (10 cm to 1 m)
- Various: wet rocks, mossy rocks, partially buried rocks
- Include rocks with soil/grass around them
- Different lighting: morning, noon, evening, overcast, shadows

**Stump (class 4)** — target: 100-300 images
- Tree stumps in fields, orchards, field boundaries
- Fresh stumps (light colored) and old stumps (dark, rotting)
- Partially hidden by grass/weeds
- Different sizes and heights
- With and without shoots growing from them

**Ditch (class 6)** — target: 100-300 images
- Irrigation ditches (most common on Indian farms!)
- Drainage ditches, field boundary channels
- Dry ditches and water-filled ditches
- Various widths (30 cm to 2 m)
- Viewed from the rover's perspective (45-60 degree downward angle)
- Include approach angles (head-on and oblique)

### Photography tips for rover-relevant data

1. **Camera height**: Mount your phone at ~40-60 cm height (rover camera level)
2. **Camera angle**: Point slightly downward (30-60°) like the rover sees
3. **Distance**: Capture at 1-5 meters (the rover's detection range)
4. **Variety**: Multiple locations, times of day, weather conditions
5. **Background**: Real farm backgrounds (soil, crops, paths, grass)
6. **Occlusion**: Partially hidden objects (grass over rocks, etc.)
7. **Hard negatives**: Include images with no obstacles (just paths/soil)

### Quick image sources (supplement only, not replacement for field photos)

- **Google Images** (for initial prototyping only - check licensing):
  - Search "rock on dirt path", "tree stump in field", "irrigation ditch India"
- **Roboflow Universe** (search for community datasets):
  - https://universe.roboflow.com/ - search "rock detection", "tree stump"
- **Pexels/Unsplash** (free commercial license):
  - Search for agricultural landscape images with these objects

---

## Step 2: Annotate Images with Bounding Boxes

### Tool: Roboflow (free tier, easiest)

1. Go to https://app.roboflow.com/ (sign up free)
2. Create a new project → "Object Detection"
3. Upload your images
4. Draw bounding boxes around each obstacle
5. Use EXACTLY these class names: `rock`, `stump`, `ditch`
6. Export as **YOLO v5 PyTorch** format
7. Download and extract into `manual_data/<class>/`

### Tool: CVAT (free, self-hosted or cloud)

1. Go to https://app.cvat.ai/ (free account)
2. Create a task → Upload images
3. Add labels: `rock` (ID 3), `stump` (ID 4), `ditch` (ID 6)
4. Annotate with bounding boxes
5. Export as **YOLO 1.1** format

### Tool: LabelImg (offline, desktop)

```bash
pip install labelImg
labelImg
```

1. Open your images folder
2. Set format to "YOLO"
3. Define classes in order: person, vehicle, animal, rock, stump, fence, ditch
4. Draw boxes, save

### YOLO annotation format reminder

Each `.txt` file = one line per object:
```
<class_id> <x_center> <y_center> <width> <height>
```

All values normalized 0-1. Example for a rock near center of image:
```
3 0.52 0.61 0.15 0.12
```

---

## Step 3: Organize Manual Data

Place annotated images in this structure:

```
training/manual_data/
├── rock/
│   ├── images/
│   │   ├── rock_001.jpg
│   │   ├── rock_002.jpg
│   │   └── ...
│   └── labels/
│       ├── rock_001.txt
│       ├── rock_002.txt
│       └── ...
├── stump/
│   ├── images/
│   │   └── ...
│   └── labels/
│       └── ...
├── fence/          (optional extra fence images)
│   ├── images/
│   │   └── ...
│   └── labels/
│       └── ...
└── ditch/
    ├── images/
    │   └── ...
    └── labels/
        └── ...
```

**Important:** The class IDs in label files MUST match:
- rock labels → class ID `3`
- stump labels → class ID `4`
- fence labels → class ID `5`
- ditch labels → class ID `6`

---

## Step 4: Run the Build Script

```bash
cd training/
python prepare_obstacle_dataset.py
```

The script will:
1. Download COCO 2017 val set (~1 GB) for person/vehicle/animal
2. Download Open Images V7 fence images (~500 MB via FiftyOne)
3. Merge your manual images from `manual_data/`
4. Create 80/10/10 train/valid/test split
5. Validate everything
6. Package as `obstacle_dataset.zip`

---

## Step 5: Upload to Colab

1. Open `training/obstacle_detection.ipynb` in Google Colab
2. Set runtime to **T4 GPU**
3. Run cells until the upload cell
4. Upload `obstacle_dataset.zip`
5. The notebook validates everything before training

---

## Alternative: Lightweight Dataset (Minimum Viable)

If you need a working prototype FAST with minimal data collection:

### Minimum viable counts per class:

| Class   | Minimum | Recommended | Source |
|---------|---------|-------------|--------|
| person  | 200     | 500         | COCO (auto) |
| vehicle | 150     | 400         | COCO (auto) |
| animal  | 150     | 400         | COCO (auto) |
| rock    | 50      | 200         | Manual |
| stump   | 50      | 200         | Manual |
| fence   | 100     | 300         | OI + manual |
| ditch   | 50      | 200         | Manual |

With only 50 images per rare class, the model will learn but have
limited real-world accuracy. Plan to supplement with active-learning
captures from the rover later (the `pi/ai/frame_capture.py` module
saves uncertain frames automatically for re-annotation).

---

## Alternative: Use FiftyOne to Grab Everything

If you have good internet and time, FiftyOne can pull from multiple sources:

```python
import fiftyone as fo
import fiftyone.zoo as foz

# Get person + vehicle + animal from COCO
coco_dataset = foz.load_zoo_dataset(
    "coco-2017",
    split="validation",
    label_types=["detections"],
    classes=["person", "car", "truck", "bus", "cow", "sheep", "horse", "dog", "cat"],
    max_samples=2000,
)

# Get fence from Open Images
oi_dataset = foz.load_zoo_dataset(
    "open-images-v7",
    split="train",
    label_types=["detections"],
    classes=["Fence"],
    max_samples=300,
)
```

Then export both as YOLO format and remap class IDs.

---

## Troubleshooting

### "Classes with ZERO annotations: ['rock', 'stump', 'ditch']"

You haven't added manual data yet. Create `manual_data/rock/`, etc.
with at least a few annotated images per class.

### COCO download is too slow (18 GB train set)

The script defaults to `val2017` (5,000 images, ~1 GB) which has enough
person/vehicle/animal for a strong prototype. Only download `train2017`
if you need more data and have bandwidth.

### FiftyOne fails / Open Images won't download

Skip it. Add fence images manually to `manual_data/fence/` instead.
Farm fences are easy to photograph yourself.

### Notebook rejects the ZIP

Common causes:
1. Class order wrong in `dataset.yaml` (must be exactly the 7 names above)
2. Label file has class IDs outside 0-6
3. Coordinates outside 0-1
4. Empty splits (train or valid has 0 images)
5. A class has zero annotations across all splits

### Model trains but has poor accuracy on rare classes

Expected with <100 images. Solutions:
1. Collect more diverse images (different lighting, angles, backgrounds)
2. Use the rover's active-learning captures to iteratively improve
3. Apply heavy augmentation (the notebook already uses mosaic + mixup)
4. Consider using synthetic data generation (place object cutouts on field backgrounds)

---

## Dataset Quality Checklist

Before uploading to Colab, verify:

- [ ] Every image has a matching `.txt` label file
- [ ] Every label uses class IDs 0-6 only
- [ ] All coordinates are normalized 0-1
- [ ] No class has zero annotations
- [ ] Train split has at least 100 images
- [ ] Valid split has at least 20 images
- [ ] `dataset.yaml` lists all 7 class names in order
- [ ] No duplicate images across train/valid/test splits
- [ ] Images are from diverse conditions (not all from one session)
