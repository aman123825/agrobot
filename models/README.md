# Models

Trained model files live here at runtime. Binaries are **gitignored** (see
`.gitignore`) — distribute them via GitHub Releases, Git LFS, or a model bucket.

Expected files (referenced by `pi/config.py` and the `pi/ai/` modules):

| File | Used by | Trained on |
|------|---------|------------|
| `yolov8n_obstacle.tflite` | `ai/obstacle_detection.py` | custom obstacle set |
| `plantvillage_mobilenetv2.tflite` | `ai/disease_detection.py` | PlantVillage (38 classes) |
| `deepweeds_yolov8n.tflite` | `ai/weed_detection.py` | DeepWeeds (9 species) |

For the Coral Edge TPU, export with the Edge-TPU compiler so the `_edgetpu.tflite`
variant can be delegated at inference time.
