# AgriRover — AI Accelerator Alternatives to the Coral USB Edge TPU

Researched 2026-07-30 (web-verified prices/benchmarks; India market). Goal:
more capability and better accuracy than the Coral USB (4 TOPS, INT8-only,
8 MB model limit, abandoned `edgetpu_compiler` toolchain) at the lowest cost.

**Key insight:** the rover only needs 5–15 FPS (it moves slowly). The reason to
upgrade is NOT speed — it is **accuracy headroom**: running YOLOv8s/YOLOv8m at
640px instead of YOLOv8n at 320–448px, running all three models concurrently,
and being on a toolchain that is still maintained.

---

## The candidates

| Option | TOPS | India price | Host needed | YOLOv8 toolchain | Verdict |
|---|---|---|---|---|---|
| Coral USB (current) | 4 (INT8) | ₹3,000–4,500 | Pi 4 USB ✓ | DIY (our `yolo_tflite.py`) | baseline, EOL ecosystem |
| **AI HAT+ 13 TOPS (Hailo-8L)** | 13 | **₹6,350** | **Pi 5 only** (PCIe) | Official model zoo, active | cheapest real upgrade |
| **AI HAT+ 26 TOPS (Hailo-8)** | 26 | **₹10,500** | **Pi 5 only** | Official, best-in-class | **best value — recommended** |
| AI HAT+ 2 (Hailo-10H, Jan 2026) | 40 + 8GB | ~$130 (India: just arriving) | Pi 5 only | Same Hailo stack + LLM/VLM | only if on-rover LLM wanted |
| Jetson Orin Nano Super devkit | 67 | ₹37,200–54,500 | **replaces Pi entirely** | Native PyTorch/TensorRT | max capability tier |
| Orange Pi 5 / RK3588 NPU | 6 | ₹8,000–12,000 (board) | replaces Pi | RKNN convert (friction) | ok, but Pi code must be ported |
| MemryX MX3 M.2 | 24 | $149 (import only) | Pi 5 + M.2 HAT | Good SDK (Phoronix praise) | watch; poor India availability |
| Sony IMX500 AI Camera | ~3 | ~₹7,000 | **works on Pi 4** ✓ | Tiny models only | not an accuracy upgrade |
| DeepX DX-M1 / Axelera / Kneron | 25+ | import only | M.2 hosts | immature/regional | skip for now |
| Pi 5 16GB CPU-only | — | ₹11,000–13,000 | — | TFLite XNNPACK | ~8–12 FPS v8n, no headroom |

Measured performance (community + vendor benchmarks):
- **Hailo-8L (13 TOPS):** YOLOv8n ~60 FPS; ~200 FPS on SSD-MobileNet (4× Coral
  on Coral's own turf); Coral ≈ 20 FPS sustained for comparison.
- **Hailo-8 (26 TOPS):** YOLOv8s @640 ≈ 80–120 FPS (batch-dependent), YOLOv8m
  ≈ 24–40 FPS real-world (community reports ~50% of Hailo's official numbers —
  still 5–10× more than the rover needs). Runs multiple models simultaneously.
  ~6–7 TOPS/W; ≤5 W — battery-friendly.
- **RK3588 (6 TOPS NPU):** YOLOv8n 53 FPS / YOLOv8s 28.5 FPS INT8 (C++ path).
- **Jetson Orin Nano Super:** any model size, FP16/INT8 TensorRT, 7–25 W
  (needs its own DC supply — power-bank feed won't cut it).

---

## Recommended tiers (total cost of change, incl. host board)

### Tier A — cheapest meaningful upgrade ≈ ₹13,500–16,500
Pi 5 (4GB ₹5,500–6,200 or 8GB ₹7,200–8,000) + **AI HAT+ 13 TOPS ₹6,350**
+ 27 W PSU ₹700–1,200 + active cooler ₹600–800.
3× Coral compute, official YOLOv8 support, live toolchain. Rover code stays
Python/OpenCV; ESP32 UART link unchanged.

### Tier B — best value (RECOMMENDED) ≈ ₹19,000–21,000
Pi 5 8GB + **AI HAT+ 26 TOPS ₹10,500** + PSU + cooler.
Runs YOLOv8s/m at 640px (real accuracy gain), all three rover models
concurrently, 6.5× Coral compute, ~5 W. This is the sweet spot — matches the
`docs/UPGRADES.md` Hailo roadmap item.

### Tier C — max capability ≈ ₹37,000–55,000
**Jetson Orin Nano Super devkit** replaces the Pi 4 entirely. 67 TOPS,
native ultralytics/PyTorch (no export gymnastics), FP16, room for
VLM/segmentation/tracking research. Costs: price, 7–25 W draw (bigger
battery), and a power-wiring change. Choose only if the project is headed
to research-grade autonomy.

**Not recommended as primary:** RK3588 boards (RKNN conversion friction + our
`pi/` code is Raspberry-Pi-specific — GPIO/picamera2 ports needed); IMX500 AI
camera (too small for accuracy gains — though it IS the only Pi-4-compatible
option); MemryX/DeepX/Axelera (India availability).

---

## Impact on the existing training/export pipeline

| Pipeline piece | Hailo path (Tier A/B) | Jetson path (Tier C) |
|---|---|---|
| Colab notebooks | unchanged (train the same) | unchanged |
| YOLO export | `.pt` → ONNX → Hailo DFC → `.hef` (or Hailo Model Zoo retrain flow) | `.pt` → `model.export(format='engine')` TensorRT |
| Disease model | SavedModel → ONNX → `.hef` | SavedModel → ONNX → TensorRT |
| `*_quant.tflite` CPU fallback | still works (Pi 5 CPU ≈ 2–3× Pi 4) | works via TFLite CPU |
| `*_edgetpu.tflite` + compiler cell | obsolete (keep Coral as spare) | obsolete |
| `pi/ai/*` detectors | add a `hailo` backend (HailoRT Python API) to the candidate chain | swap to ultralytics backend (already supported in our dual-backend design) |
| ESP32 firmware / UART bridge | unchanged | unchanged (USB port exists) |

Sources: Seeed Studio Hailo benchmarks, Raspberry Pi forums AI HAT+ threads,
Jeff Geerling AI Kit review, Silverline/robu.in/IndiaMART/ThinkRobotics India
pricing, Q-engineering RK3588 benchmarks, Phoronix MemryX MX3 review,
Tom's Hardware MemryX launch coverage. Prices are indicative — reverify
before ordering.
