# Training

Model training runs on Google Colab (free T4 GPU, BOM #110). Each notebook
covers the full pipeline from dataset loading to Edge TPU compilation.

## Hardware Requirements

- Google Colab with **T4 GPU** runtime (free tier sufficient)
- ~10 GB Google Drive space for datasets and checkpoints
- Edge TPU compiler runs within Colab (installed automatically)

## Notebooks

### 1. `disease_classification.ipynb`

Fine-tunes a MobileNetV2 model on the PlantVillage dataset for crop disease
classification (38 classes across 14 crops).

**Pipeline:**
- Loads PlantVillage from `tensorflow_datasets`
- Applies augmentation (RandomFlip, RandomRotation, RandomZoom, RandomContrast)
- Two-phase training: frozen base feature extraction, then top-layer fine-tuning
- Evaluates with confusion matrix and classification report
- Exports float16 and full INT8 quantized TFLite models
- Compiles INT8 model for Coral Edge TPU

**Output files:**
| File | Description | Deploy to |
|------|-------------|-----------|
| `disease_model_float16.tflite` | CPU fallback model | `models/disease_model_float16.tflite` |
| `disease_model_quant_edgetpu.tflite` | Edge TPU model | `models/disease_model_quant_edgetpu.tflite` |

### 2. `weed_detection.ipynb`

Trains a YOLOv8n bounding-box model on the public Crop and Weed Detection
dataset (2 classes: `crop`, `weed`). The original DeepWeeds dataset is not
used because it supplies image-level classification labels, not bounding boxes.

**Pipeline:**
- Downloads the 1,300-image public Kaggle dataset without a placeholder API key
- Creates deterministic 80/10/10 train/validation/test splits
- Validates every YOLO annotation, class ID, normalized box, and split
- Trains YOLOv8n with augmentation (mosaic, mixup, HSV)
- Validates with mAP50, mAP50-95, precision, and recall metrics
- Exports calibrated full-INT8 CPU TFLite and Coral Edge TPU variants
- Verifies NHWC input and raw YOLO output compatibility with the Pi decoder

**Output files:**
| File | Description | Deploy to |
|------|-------------|-----------|
| `weed_model_quant.tflite` | INT8 CPU fallback | `models/weed_model_quant.tflite` |
| `weed_model_quant_edgetpu.tflite` | Edge TPU model | `models/weed_model_quant_edgetpu.tflite` |
| `weed_labels.txt` | `crop`, `weed` in model order | `models/weed_labels.txt` |

### 3. `obstacle_detection.ipynb`

Trains a YOLOv8n model for real-time obstacle detection with 7 classes:
person, vehicle, animal, rock, stump, fence, ditch.

**Pipeline:**
- Uploads one prepared YOLO dataset ZIP and verifies its exact seven-class order
- Rejects missing labels, malformed rows, invalid boxes, empty splits, and absent classes
- Trains from COCO pretrained weights with augmentation tuned for outdoor scenes
- Evaluates overall and per-class mAP metrics
- Exports calibrated full-INT8 CPU TFLite and Coral Edge TPU variants
- Verifies tensor compatibility with `pi/ai/yolo_tflite.py`
- Requires real on-device benchmarking instead of claiming Coral FPS from a Colab GPU

**Output files:**
| File | Description | Deploy to |
|------|-------------|-----------|
| `obstacle_model_quant.tflite` | INT8 CPU fallback | `models/obstacle_model_quant.tflite` |
| `obstacle_model_quant_edgetpu.tflite` | Edge TPU model | `models/obstacle_model_quant_edgetpu.tflite` |
| `obstacle_labels.txt` | Seven labels in model order | `models/obstacle_labels.txt` |

## Datasets

- **PlantVillage** - 54,000+ images, 14 crops, 38 disease classes (disease model)
- **Crop and Weed Detection Data with Bounding Boxes** - 1,300 images, `crop`/`weed` boxes (starter weed model)
- **Custom obstacles** - User-collected + legally usable public subsets (obstacle model)

## Workflow

1. Open the notebook in Google Colab (set runtime to GPU/T4).
2. Run all cells sequentially; the notebooks validate data before starting training.
3. Download both the INT8 CPU fallback and Edge TPU compiled `.tflite` files plus labels.
4. Copy artifacts to `models/` on the Raspberry Pi (see `models/README.md`).
5. Benchmark on the actual Pi/Coral and complete the safety checks in `TRAIN_WEED_AND_OBSTACLE_MODELS.md`.

## QAT / calibration stage (optional, docs/UPGRADES.md §2)

Each notebook now ends with an optional add-on section that starts from the
existing best checkpoint (no retraining) and re-exports the **same** output
filenames, so the Pi detectors need zero changes.

- **`disease_classification.ipynb` — "Optional: quantization-aware fine-tune
  (QAT)"**: real QAT via `tensorflow-model-optimization`. Loads
  `best_disease_model.keras` (or the in-session model), wraps it with
  fake-quant nodes (whole model, falling back to the Dense head if the
  MobileNetV2 base refuses), fine-tunes 3-5 epochs at LR 1e-5 on the same
  seed-42 split, rewrites `output/disease_model_quant.tflite`, saves
  `best_disease_model_qat.keras`, and prints PTQ-vs-QAT INT8 test accuracy
  side by side. **Runtime: T4 GPU (or CPU) — not the TPU runtime** (tfmot QAT
  is not TPU-compatible; the cells warn and fall back if a TPU is detected).
  Re-run the existing `edgetpu_compiler` and download cells afterwards.
- **`weed_detection.ipynb` / `obstacle_detection.ipynb` — "Optional:
  quantization-cost check and QAT notes"**: ultralytics has no first-class QAT
  API, and the INT8 exports already calibrate on the full dataset
  (`data=` + `fraction=1.0`), so these sections *measure* the quantization
  cost instead: FP32 `best.pt` vs the deployed INT8 `.tflite`, validated on
  the same val split at 320 px, with the mAP drop printed. A resolver cell
  finds the in-session/on-disk `best.pt` or accepts an upload. **Runtime: T4
  GPU** (the INT8 val leg runs on CPU). If the drop exceeds ~2-3 mAP50
  points, the markdown explains what a true PyTorch QAT loop would require.

**When to run:** after the normal train + export cells (same session), or in a
fresh session after re-running the setup/dataset/export cells. **Expected
outcome:** disease — QAT INT8 accuracy at or above the PTQ number (recovers
most of the PTQ loss); YOLO models — a measured PTQ cost, typically under
0.02-0.03 mAP50, confirming PTQ is sufficient.

## Model-to-Module Mapping

| Model file | Pi module | Class |
|------------|-----------|-------|
| `models/disease_model_quant_edgetpu.tflite` | `pi/ai/disease_detection.py` | `DiseaseClassifier` |
| `models/weed_model_quant_edgetpu.tflite` | `pi/ai/weed_detection.py` | `WeedDetector` |
| `models/obstacle_model_quant_edgetpu.tflite` | `pi/ai/obstacle_detection.py` | `ObstacleDetector` |

## Hailo `.hef` export (primary platform — Pi 5 + Hailo-8 AI HAT+)

The rover's primary edge-AI platform is the Pi 5 + Hailo-8 AI HAT+
(`docs/accelerator-alternatives.md` Tier B). The detectors load a Hailo `.hef`
first (`pi/ai/hailo_backend.py`), then fall back to the Coral/CPU `.tflite`
files these notebooks already produce. **Training does not change** — only one
export stage is added, run on an x86 Linux machine (not the Pi, not Colab's
GPU runtime — the Hailo Dataflow Compiler is x86-Linux only):

```bash
# 1. Export the trained YOLO to ONNX (opset 11, static shapes) from best.pt:
yolo export model=best.pt format=onnx opset=11 imgsz=320

# 2. Install the Hailo AI SW Suite (Dataflow Compiler + Model Zoo) on x86 Linux
#    (free developer account at hailo.ai), then compile ONNX -> .hef:
hailomz compile yolov8n --ckpt best.onnx --hw-arch hailo8 \
    --calib-path calib_images/ --classes <N>

# 3. Rename to the candidate filename the detector expects and deploy:
#    obstacle_model.hef / weed_model.hef  ->  models/
```

Notes:
- Use `--hw-arch hailo8` for the 26-TOPS HAT, `hailo8l` for the 13-TOPS HAT.
- Calibration images: reuse the training/val set (a few hundred is plenty).
- The `.hef` output tensor is the same raw YOLOv8 head the Pi decoder expects,
  so `pi/ai/hailo_backend.py` reuses the identical NMS/decode as the TFLite path.
- The disease MobileNetV2 classifier stays on TFLite/Coral for now; a Hailo
  classification backend is a small future addition.
- Keep the Coral `*_edgetpu.tflite` and CPU `*_quant.tflite` exports too — they
  are the documented fallback and the CI/desktop test path.
