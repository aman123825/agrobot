# Train the Weed and Obstacle Models

The two notebooks have been corrected and checked against the Raspberry Pi inference code:

- `training/weed_detection.ipynb`
- `training/obstacle_detection.ipynb`

Run them separately in Google Colab. Do not run both in the same session unless you intentionally clear the previous model and dataset files.

## Errors that were fixed

1. The original DeepWeeds dataset is an image-classification dataset, not an object-detection dataset. It has image-level species labels but no bounding boxes, so it could not train the rover's bounding-box spraying pipeline.
2. The old weed notebook depended on an unverified Roboflow workspace/project/version and a placeholder API key.
3. The old weed class list did not match a verified public bounding-box dataset.
4. The obstacle notebook created empty folders but had no working upload/extraction path.
5. Neither notebook fully validated missing labels, malformed YOLO rows, invalid normalized boxes, empty splits, or classes with no objects before training.
6. INT8 exports did not explicitly use the training dataset for quantization calibration and could silently calibrate with the wrong default dataset.
7. The old manual Edge TPU compiler installation used deprecated `apt-key` commands and ambiguous file selection. The corrected notebooks use Ultralytics' `format="edgetpu"` export directly; it auto-installs the compiler in Colab when needed and leaves both the uncompiled INT8 CPU model and Coral-compiled model.
8. Export filenames were ambiguous and the CPU fallback files were not consistently downloaded.
9. `models/obstacle_labels.txt` was missing; only `obstacle_labels before.txt` existed.
10. The Pi weed detector previously treated every non-`negative` class as sprayable. It now ignores `crop`, so the new two-class model sprays only detections labeled `weed`.
11. The notebooks attempted to prefer an end-to-end model generation while the Pi decoder expects the raw YOLO detection head. The corrected notebooks use YOLOv8n for compatibility.
12. The obstacle notebook's claimed Coral FPS was an estimate based on a PyTorch GPU benchmark. The corrected workflow requires measuring on the actual Raspberry Pi and Coral.

---

# A. Weed model: complete steps

## 1. Open the corrected notebook

1. Go to <https://colab.research.google.com/>.
2. Choose **File > Upload notebook**.
3. Upload `training/weed_detection.ipynb`.
4. Choose **Runtime > Change runtime type**.
5. Select **T4 GPU** and save.

## 2. Run installation and GPU checks

Run the cells from the top in order.

The import cell must print a GPU name. If it raises:

```text
GPU not enabled
```

return to **Runtime > Change runtime type > T4 GPU**.

## 3. Download and prepare the dataset

The notebook automatically downloads the verified public Kaggle dataset:

```text
ravirajsinh45/crop-and-weed-detection-data-with-bounding-boxes
```

It contains:

- 1,300 images
- YOLO bounding-box annotations
- class 0: `crop`
- class 1: `weed`

The notebook makes a deterministic split:

- 80% training: 1,040 images
- 10% validation: 130 images
- 10% test: 130 images

No Kaggle API token should be required for this public dataset. If Kaggle temporarily rejects the download, rerun only the download cell.

## 4. Check dataset validation output

Before training, the validator must finish without an exception and print image/object counts.

Stop and fix the dataset if it reports any of these:

- missing image or label directory
- missing `.txt` label for an image
- a label row with anything other than five values
- a non-numeric label value
- class ID outside 0-1
- coordinates outside 0-1
- zero or negative width/height
- an empty train or validation split
- a class with no labeled objects

## 5. Train

Run the training cell. Its important settings are:

```text
model: YOLOv8n
image size: 640
batch: 16
epochs: 100
early-stopping patience: 20
```

If Colab reports CUDA out-of-memory:

1. Change `batch=16` to `batch=8`.
2. Rerun the model setup cell.
3. Rerun the training cell.

Do not reduce the export image size below 320 without testing field accuracy.

## 6. Review validation

The validation cell prints:

- mAP50
- mAP50-95
- precision
- recall
- result plots and confusion matrix when available

Also inspect the six held-out sample images. Check especially that crops are labeled `crop` and unwanted plants are labeled `weed`.

Do not deploy only because training completed. Collect rover-camera images and fine-tune later; this public dataset is a starter dataset and may not match your crops, camera angle, soil, lighting, or local weeds.

## 7. Export CPU and Coral models

Run the export cell. A single `format="edgetpu"` export creates the uncompiled full-INT8 TFLite file and the Coral-compiled file; the notebook copies them to:

```text
weed_model_quant.tflite
weed_model_quant_edgetpu.tflite
```

The export uses:

```text
input size: 320 x 320
batch: 1
INT8 calibration data: the weed training dataset
```

The next cell verifies the CPU model has NHWC input `(1, 320, 320, 3)` and a raw YOLO output channel dimension of `4 + number_of_classes`, which is required by `pi/ai/yolo_tflite.py`. Do not substitute the newer standalone `format="litert"` CPU export without updating the Pi backend because current LiteRT exports use NCHW input.

The Edge TPU export must run on Colab's x86 Linux environment. Do not compile it on the Raspberry Pi ARM system.

## 8. Verify and download

Run the verification and download cells. Download all four files:

```text
weed_model_quant.tflite
weed_model_quant_edgetpu.tflite
weed_labels.txt
best.pt
```

The labels file must contain exactly:

```text
crop
weed
```

## 9. Deploy

Copy these files into the project `models/` directory:

```text
models/weed_model_quant.tflite
models/weed_model_quant_edgetpu.tflite
models/weed_labels.txt
```

Keep `best.pt` separately as the retraining/debug checkpoint. The Pi does not need it when TFLite works.

## 10. Test on the Raspberry Pi

From the repository root on the Pi:

```bash
python3 pi/ai/benchmark.py --image path/to/real_field_image.jpg --iters 50
```

Confirm the logs include:

```text
WeedDetector: TFLite backend ready
```

Safety test before connecting the chemical pump:

1. Disable or physically disconnect the spray output.
2. Test multiple crop-only images; they must not trigger a weed result.
3. Test weed images at different sizes and positions.
4. Test sunlight, shade, blur, wet soil, crop residue, and partial occlusion.
5. Reconnect spraying only after false-positive behavior is acceptable.

---

# B. Obstacle model: complete steps

## 1. Prepare the obstacle dataset first

Unlike the weed notebook, the obstacle notebook cannot invent a correct seven-class safety dataset. Prepare and annotate images before opening Colab.

Required class IDs and order:

```text
0 person
1 vehicle
2 animal
3 rock
4 stump
5 fence
6 ditch
```

Recommended sources:

- rover-camera field captures for every class
- legally usable public datasets for person, vehicle, and animal examples
- your own field images for rock, stump, fence, and especially ditch
- hard negatives: crops, weeds, shadows, tools, irrigation pipes, puddles, soil clods, and empty paths

For a usable prototype, target at least several hundred labeled instances per class. More important than raw count is coverage of distance, direction, lighting, size, occlusion, and camera motion.

## 2. Create the required ZIP

Use YOLO detection labels. Each line must be:

```text
<class_id> <x_center> <y_center> <width> <height>
```

All four box coordinates must be normalized from 0 to 1.

Create this structure:

```text
obstacle_dataset.zip
  dataset.yaml
  train/
    images/
    labels/
  valid/
    images/
    labels/
  test/
    images/
    labels/
```

Use approximately:

- 80% train
- 10% validation
- 10% test

Do not put neighboring frames from the same short video into different splits. Split by capture session/location to prevent data leakage.

Use this `dataset.yaml`:

```yaml
path: .
train: train/images
val: valid/images
test: test/images
nc: 7
names:
  - person
  - vehicle
  - animal
  - rock
  - stump
  - fence
  - ditch
```

## 3. Open the corrected notebook

1. Open Google Colab.
2. Upload `training/obstacle_detection.ipynb`.
3. Set **Runtime > Change runtime type > T4 GPU**.
4. Run the installation and import cells.

## 4. Upload the ZIP

Run the upload cell and select exactly one file: `obstacle_dataset.zip`.

The next cell locates `dataset.yaml`, verifies the exact seven-class order, and writes an absolute Colab dataset configuration.

## 5. Pass all dataset checks

The validation cell checks every image and annotation before training.

Do not bypass this cell. It catches:

- missing train, validation, or test directories
- image-label filename mismatches
- malformed annotation rows
- class IDs outside 0-6
- invalid boxes
- empty train/validation splits
- a class with zero labeled objects

If the class-order assertion fails, correct the annotation IDs or dataset YAML. Do not merely reorder the names if the numeric IDs in the label files have a different meaning.

## 6. Train

The training cell uses:

```text
model: YOLOv8n
image size: 640
batch: 16
epochs: 150
early-stopping patience: 25
```

If CUDA memory is insufficient, reduce `batch` to 8. If small rocks or distant objects are missed, first improve annotations/data; then consider keeping 640 for export or testing a larger model. Remember that a larger model may not fully map to the Edge TPU and can increase latency.

## 7. Evaluate as a safety model

Review overall and per-class AP50. Pay special attention to recall for:

- person
- animal
- ditch

A high overall mAP can hide poor recall for one critical class. Also inspect false negatives manually on the test set.

Do not declare the model safe based only on Colab metrics. The rover also uses the ToF sensor and fail-safe stop logic; camera detection is one layer, not the sole safety mechanism.

## 8. Export CPU and Coral models

Run the export cell. A single Edge TPU export creates both the uncompiled INT8 CPU fallback and the Coral-compiled file; the notebook copies them to:

```text
obstacle_model_quant.tflite
obstacle_model_quant_edgetpu.tflite
```

It uses the obstacle dataset for INT8 quantization calibration and 320 x 320 input. The following verification cell checks the NHWC input and raw YOLO output tensor contract required by the Pi decoder.

## 9. Verify and download

Download:

```text
obstacle_model_quant.tflite
obstacle_model_quant_edgetpu.tflite
obstacle_labels.txt
best.pt
```

The labels file must contain exactly the seven class names in ID order.

## 10. Deploy

Copy into `models/`:

```text
models/obstacle_model_quant.tflite
models/obstacle_model_quant_edgetpu.tflite
models/obstacle_labels.txt
```

## 11. Bench and perform safe physical tests

Run:

```bash
python3 pi/ai/benchmark.py --image path/to/obstacle_test.jpg --iters 50
```

Confirm:

```text
ObstacleDetector: TFLite backend ready
```

Then test with the rover wheels lifted, drive power disconnected, or the rover on blocks:

1. Present every obstacle class at several distances.
2. Confirm STOP is issued when the ToF distance is below 400 mm.
3. Confirm a camera detection with unavailable ToF distance also causes STOP.
4. Test partial persons/animals at frame edges.
5. Test ditch approaches from different angles.
6. Test false positives on crops, shadows, puddles, and rough soil.
7. Only perform low-speed ground tests after all stationary tests pass.

---

# Final model directory checklist

After both notebooks are trained and deployed, `models/` should contain:

```text
weed_model_quant.tflite
weed_model_quant_edgetpu.tflite
weed_labels.txt
obstacle_model_quant.tflite
obstacle_model_quant_edgetpu.tflite
obstacle_labels.txt
disease_model_quant.tflite
disease_model_quant_edgetpu.tflite
disease_model_float16.tflite
plantvillage_labels.txt
```

Use the CPU `*_quant.tflite` files as fallbacks. Coral-compiled `*_edgetpu.tflite` files cannot run on a plain CPU interpreter.
