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

Trains a YOLOv8n model on the DeepWeeds dataset for weed species detection
(9 classes).

**Pipeline:**
- Downloads DeepWeeds dataset from Roboflow in YOLO format
- Configures dataset YAML with class names
- Trains YOLOv8n from COCO pretrained weights with augmentation (mosaic, mixup, HSV)
- Validates with mAP50, mAP50-95, precision, and recall metrics
- Exports to TFLite with INT8 quantization
- Compiles for Edge TPU
- Includes inference demo on sample images

**Output files:**
| File | Description | Deploy to |
|------|-------------|-----------|
| `weed_model_quant_edgetpu.tflite` | Edge TPU model | `models/weed_model_quant_edgetpu.tflite` |

### 3. `obstacle_detection.ipynb`

Trains a YOLOv8n model for real-time obstacle detection with 7 classes:
person, vehicle, animal, rock, stump, fence, ditch.

**Pipeline:**
- Sets up custom dataset structure with YOLO annotation format
- Documents annotation format and class definitions
- Trains from COCO pretrained weights with augmentation tuned for outdoor scenes
- Evaluates with per-class mAP metrics
- Exports to both TFLite (Edge TPU) and ONNX formats
- Includes real-time inference benchmark (target: >=15 FPS)
- Documents integration with `pi/ai/obstacle_detection.py`

**Output files:**
| File | Description | Deploy to |
|------|-------------|-----------|
| `obstacle_model_quant_edgetpu.tflite` | Edge TPU model | `models/obstacle_model_quant_edgetpu.tflite` |
| `obstacle_model.onnx` | ONNX format (desktop debugging) | `models/obstacle_model.onnx` |

## Datasets

- **PlantVillage** - 54,000+ images, 14 crops, 38 disease classes (disease model)
- **DeepWeeds** - 17,509 images, 9 weed species (weed model)
- **Custom obstacles** - User-collected + COCO/Open Images subsets (obstacle model)

## Workflow

1. Open the notebook in Google Colab (set runtime to GPU/T4).
2. Run all cells sequentially. Training takes 30-90 minutes per notebook.
3. Download the Edge TPU compiled `.tflite` files.
4. Copy artifacts to `models/` on the Raspberry Pi (see `models/README.md`).
5. Restart the relevant AgroBot service to load the new model.

## Model-to-Module Mapping

| Model file | Pi module | Class |
|------------|-----------|-------|
| `models/disease_model_quant_edgetpu.tflite` | `pi/ai/disease_detection.py` | `DiseaseClassifier` |
| `models/weed_model_quant_edgetpu.tflite` | `pi/ai/weed_detection.py` | `WeedDetector` |
| `models/obstacle_model_quant_edgetpu.tflite` | `pi/ai/obstacle_detection.py` | `ObstacleDetector` |
