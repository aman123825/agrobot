# Training

Model training runs on Google Colab (free T4 GPU, BOM #110). Add notebooks here.

## Datasets
- **PlantVillage** — 54,000+ images, 14 crops, 38 disease classes (disease model).
- **DeepWeeds** — 17,509 images, 9 weed species (weed model).

## Workflow
1. Load datasets from Google Drive in Colab.
2. Fine-tune (MobileNetV2 for disease; YOLOv8n for obstacle/weed).
3. Export to `.tflite`; compile the Edge-TPU variant for Coral.
4. Copy artifacts into `models/` on the Pi (see `models/README.md`).
