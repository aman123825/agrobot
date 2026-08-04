# AgriRover — Upgrades & Advancements Roadmap

Complete register of fixes, upgrades, and advancement options for the AI stack
and the platform around it. Compiled July 2026. Each item lists what it buys,
what it costs (money/effort), and its priority.

Priorities: **P0** = blocks the AI from working at all · **P1** = big win, do
next · **P2** = strong upgrade once P0/P1 land · **P3** = future/ambitious.

---

## 0. Fixes already applied (July 2026)

These are in the codebase now — no action needed, listed for the record:

| Fix | Files |
|-----|-------|
| YOLO models can now run on the Coral / plain TFLite (numpy decode + NMS, no ultralytics needed on the Pi) | `pi/ai/yolo_tflite.py` (new) |
| Model filename mismatch resolved: detectors try the training-notebook output names first, then CPU variants, then legacy `.pt` | `pi/ai/obstacle_detection.py`, `pi/ai/weed_detection.py`, `pi/ai/disease_detection.py` |
| DeepWeeds `negatives` (not-a-weed) class can no longer trigger the sprayer | `pi/ai/weed_detection.py` |
| Class label files committed (obstacle 7, weed 9, PlantVillage 38) | `models/*_labels.txt` |
| Disease notebook now exports `plantvillage_labels.txt` in authoritative tfds order | `training/disease_classification.ipynb` |
| `models/README.md` rewritten with the real candidate-file table | `models/README.md` |
| Undistorter wired into the orchestrator frame loop | `pi/main.py` |
| VL53L1X ToF module added and wired: obstacle stops use the real 400 mm rule; spray aiming gets target depth | `pi/sensors/tof.py` (new), `pi/main.py` |
| Encoder odometry + GPS now feed the pose EKF; plant geo-tags use the EKF pose in a first-fix-anchored local frame | `pi/main.py`, `pi/config.py` (`TRACK_WIDTH_M`, `GPS_VAR_M2`) |
| Weed-size-scaled spray dose: burst 0.3–1.2 s by bbox area | `pi/main.py` (`spray_duration_s`) |
| Active-learning frame capture: low-confidence + periodic frames saved with JSON sidecars, rate/file-capped | `pi/ai/frame_capture.py` (new), `pi/main.py` |
| On-device inference benchmark (`python pi/ai/benchmark.py`) with JSONL history | `pi/ai/benchmark.py` (new) |
| Weed + obstacle notebooks train YOLO26n (fallback YOLOv8n); ultralytics unpinned to ≥ 8.4 | `training/weed_detection.ipynb`, `training/obstacle_detection.ipynb` |
| paho import made lazy so pipeline/orchestrator import cleanly without it | `pi/bridge/mqtt_client.py` |
| Test suite: 47 tests over aiming, tagging, EKF, geo, planner, YOLO decode, capture, stream stats, heatmap, scheduler | `pi/tests/` (new) — run `py -3.14 -m pytest pi/tests` |
| Field-health telemetry: CPU temp, undervoltage/throttle flags, disk, boot counter sampled every 30 s → `rover/<id>/health` MQTT + Telegram alert on status transitions (farmer-needs-and-durability.md §2.2) | `pi/monitor/health.py` (new), `pi/main.py`, `pi/config.py` |
| Per-acre chemical-savings proof: spot-spray litres vs broadcast baseline (default 100 L/acre), % and ₹ saved, Hindi/English farmer summary pushed at mission end + season totals JSONL (§1.3 "that number is the sales pitch") | `pi/data/savings.py` (new), `pi/main.py` |
| Two-way Telegram control: /stop /go /status /photo /summary, chat-ID allowlist (fail closed, `TELEGRAM_ALLOWED_CHAT_IDS`), remote-stop latch that obstacle-clear auto-resume cannot undo; alerter now stdlib-only (no `requests`) | `pi/alerts/telegram_bot.py`, `pi/main.py` |
| Deployment hardened: Mosquitto TLS+auth (8883 + loopback-only 1883, anonymous off), CA/cert generator, systemd `Restart=always` + `/etc/agrirover.env`, opt-in hardware watchdog and SD-protect (noatime, volatile journald, tmpfs /var/log, OverlayFS guidance) | `deploy/` — see `deploy/README.md` |
| Test suite grown to 117 tests (health, savings, telegram) | `pi/tests/` |
| ISOXML export: prescription maps now emit ISO 11783-10 TASKDATA sets (TASKDATA.XML + GridType-2 binary, zip option) loadable by commercial tractor terminals; conventions audited in the module docstring | `pi/data/isoxml.py` (new), `pi/data/prescription_map.py` (`to_isoxml`) |
| Model versioning & OTA: sha256 manifest generator + atomic pull-verify-swap updater with `.bak` rollback, weekly systemd timer (no-op until `MODEL_MANIFEST_URL` set) | `pi/ai/model_ota.py` (new), `deploy/systemd/agrobot-model-ota.{service,timer}`, `deploy/README.md` §Model OTA |
| Test suite grown to 147 tests (isoxml, model OTA) | `pi/tests/` |
| QAT / calibration stage appended to the notebooks: disease gets a real tfmot QAT fine-tune (loads `best_disease_model.keras`, TPU-detects and falls back, re-exports the same filenames, prints PTQ-vs-QAT accuracy); YOLO notebooks get a measured fp32-vs-int8 mAP comparison + honest QAT notes (ultralytics has no QAT API) — run on Colab when retraining | `training/*.ipynb`, `training/README.md` |
| Pi 5 + Hailo-8 AI HAT+ set as the primary platform: `hailo_backend.py` (HailoRT YOLO, same detection-dict contract as `yolo_tflite.py`, guarded imports) added; detectors try `*.hef` first then fall back to Coral/CPU `*.tflite`; `USE_HAILO` config flag; docs (README, shopping-list, circuit-diagram, BUILD) updated. Coral/Pi 4 remain the documented fallback | `pi/ai/hailo_backend.py` (new), `pi/ai/obstacle_detection.py`, `pi/ai/weed_detection.py`, `pi/config.py` |

## 1. P0 — Train and deploy the three models

**The single blocking item: `models/` has no trained models.** Everything
downstream (obstacle stops, spot spray, disease tagging) is inert until this
is done. The notebooks are complete — run them on Colab (free T4):

1. `training/disease_classification.ipynb` — PlantVillage MobileNetV2 (~30–60 min)
2. `training/weed_detection.ipynb` — DeepWeeds YOLOv8n (~60–90 min)
3. `training/obstacle_detection.ipynb` — custom 7-class YOLOv8n (**needs a
   dataset first** — collect/annotate field images, or bootstrap from COCO/Open
   Images subsets for person/vehicle/animal)
4. Drop the exported files into `models/` per `models/README.md`. Zero code
   changes needed — the detectors pick them up by filename.

Also quick, free, and unblocked:
- **Camera calibration**: print a checkerboard, run
  `ai/camera_calib.calibrate_from_images()` — the 160° lens badly needs
  undistortion for accurate aiming and geo-tagging. (The `Undistorter` and the
  ToF distance are now wired into `pi/main.py` — see §0 — so calibration is
  the only remaining manual step.)

## 2. Model upgrades (P1)

| Upgrade | Why | Notes |
|---------|-----|-------|
| **YOLOv8n → YOLO26n** | Released Jan 2026, edge-first: NMS-free end-to-end inference (deterministic latency), DFL removed for clean quantized exports, ~31–43 % faster on CPU, +mAP over YOLO11n. Drop-in via ultralytics API, so the notebooks change ~1 line (`yolo26n.pt`). | AGPL-3.0 license — fine for a college/pitch project; for a commercial product consider Apache-2.0 **RF-DETR** (Roboflow) instead. |
| **Quantization-aware training (QAT)** | INT8 post-training quantization (current notebooks) costs a few mAP points; QAT recovers most of it. | Notebook stage ADDED (§0): disease = tfmot QAT fine-tune; YOLO = measured PTQ cost + full-yaml calibration (ultralytics has no QAT API — true YOLO QAT needs a custom torch.ao loop). Run it on the next Colab retrain. |
| **Weed segmentation instead of boxes** | Segmentation masks → weed *centroid + area* → better aim + dose scaling per weed size. YOLO26-seg / YOLOv8n-seg. | Needs mask labels; Roboflow-format DeepWeeds derivatives exist. |
| **India-relevant fine-tuning** | PlantVillage is lab-style leaf photos; DeepWeeds is Australian rangeland species. Field accuracy will drop hard. Fine-tune on locally collected images of the actual target crops/weeds. | Highest-leverage accuracy item. Start collecting frames from day one (see §8 active learning). |
| **Field-condition robustness** | Shadow/lighting bias is a known failure mode of field weed detection (see arXiv 2508.19511 semi-supervised framework). Add heavy lighting/shadow augmentation; capture at multiple times of day. | Cheap: augmentation config only. |
| **Disease detection → detection, not full-frame classify** | Current pipeline classifies the whole frame and fakes a centered bbox for geo-tagging. A leaf/plant detector (or YOLO26 with disease classes) localizes actual diseased plants → real per-plant tags. | Medium effort, big data-quality win. |

## 3. Edge compute hardware (SELECTED: Pi 5 + Hailo-8)

**DECISION (docs/accelerator-alternatives.md Tier B):** the primary platform is
now the **Pi 5 + Hailo-8 AI HAT+ (26 TOPS)**. `pi/ai/hailo_backend.py` is wired
in (detectors load `*.hef` first), `USE_HAILO` defaults on, and the docs/BOM are
updated. The Pi 4 + Coral USB (4 TOPS) remains the documented fallback / working
prototype. The Coral ecosystem is effectively end-of-life (last library updates
years ago; PyCoral pinned to old Python), which is why the primary path moved to
the actively-maintained Hailo toolchain.

| Option | TOPS | ~Cost | Verdict |
|--------|------|-------|---------|
| Keep Pi 4 + Coral | 4 | owned | Works for MobileNet/YOLOv8n-320. Fine for the demo; dead end for growth. |
| **Pi 5 + AI HAT+ (Hailo-8L)** | 13 | ~$70 + Pi 5 | First-party, kernel-supported, well documented. |
| **Pi 5 + AI HAT+ (Hailo-8)** | 26 | ~$110 + Pi 5 | **Recommended upgrade.** YOLOv8n @640 runs 130–160 FPS (vs ~30 FPS Coral @320). ~2.5 W. Headroom for seg + multiple models concurrently. |
| Raspberry Pi **AI Camera (Sony IMX500)** | on-sensor | ~$70 | Inference *inside the camera*, zero Pi CPU load; good as a second "smart eye" (e.g. dedicated weed cam on the spray boom). |
| Hailo-10H | 40 (INT4) | new, shipping since mid-2025 | Enables small on-device generative/VLM workloads; watch this space. |
| Jetson Orin Nano Super | 67 | ~$249 | Only if moving to heavy models / SLAM / ROS 2 perception stacks. |

Migration cost: Hailo uses `.hef` compiled models (their Dataflow Compiler),
not TFLite — one extra export stage in the notebooks; `pi/ai/` would get a
`hailo_backend.py` sibling to `yolo_tflite.py` (same detection dict schema, so
detectors and orchestrator don't change).

## 4. Perception & sensing (P2)

- **Depth camera (OAK-D Lite, ~$150)**: stereo depth + on-device NN. Replaces
  the single-point VL53L1X with a full depth map → per-detection distance,
  obstacle *avoidance* (not just stop), and 3-D weed positions for aiming.
- **NDVI / multispectral (Pi NoIR camera + blue filter, ~$30)**: crop-stress
  heatmaps before disease is visible to RGB. Proven low-cost designs exist
  (Plant Methods 2023 low-cost NDVI imaging system). Feeds a "stress layer"
  next to the existing soil heatmap.
- **Night operation**: IR illuminator + NoIR camera; note edge-accelerator
  models degrade at night without IR-tuned training data.
- **Second camera on the tool row** (or the IMX500 smart camera) so detection
  and actuation don't share one wide-angle view.

## 5. Navigation & autonomy (P1 for RTK, P2–P3 for the rest)

- **RTK GNSS (P1)**: Neo-6M is ~1–2.5 m; row-following and per-plant revisits
  need centimeters. u-blox **ZED-F9P** rover (simpleRTK2B/Waveshare HAT +
  multiband antenna) ≈ **$250–450**, 1 cm with corrections. Free public NTRIP
  casters exist in many regions (India: CORS network via SoI). The EKF
  (`pi/nav/ekf.py`) already takes GPS variance — plug the RTK fix straight in.
- **Wheel-odometry + GPS fusion is now live** — the orchestrator dead-reckons
  the EKF from the encoders every frame and corrects it with each GPS fix
  (§0); dropping in an RTK receiver only requires lowering `GPS_VAR_M2`.
- **Obstacle avoidance vs stop (P2)**: with depth (OAK-D) or the ToF sweep,
  steer around static obstacles instead of halting the mission.
- **ROS 2 Nav2 (P3)**: the `ros2/` package already mirrors the AI nodes;
  adopting Nav2 gives costmaps, planners, and recovery behaviors for free —
  at the price of running the full ROS 2 stack on the Pi.
- **Multi-rover / swarm coordination (P3)**: MQTT topics are already
  namespaced per `ROVER_ID` — a fleet dashboard is mostly UI work.

## 6. Actuation & weeding tech (P2–P3)

- **Dose scaling by weed size** — DONE (§0): burst duration now scales
  0.3–1.2 s with bbox area; a future segmentation model refines the area
  estimate.
- **Mechanical weeding attachment** (P2): the modular-attachment design
  already anticipates it; AI-guided hoe/tine for herbicide-free rows.
  Commercial art: FarmDroid FD20 (solar, seed-position-based weeding).
- **Laser weeding (P3)**: the research frontier (Carbon Robotics LaserWeeder;
  "LiteWeed" shows a Pi-5-class laser platform in academia). Serious safety
  engineering (interlocks, shrouding, eye safety) required — treat as a
  research track, not a bolt-on.
- **Electric/thermal weeding (P3)**: alternative chemical-free kill mechanisms
  appearing in 2025–26 commercial robots (AgriPass pulls weeds robotically).

## 7. Data platform & analytics (P2)

- **Pathway-native pipeline**: `pipeline/pathway_stream.py` is a stdlib
  re-implementation; port to actual Pathway operators (windowed joins,
  `pw.io.mqtt`) for exactly-once semantics and richer windows. The MQTT/CSV
  contract is already stable, so it's a drop-in swap.
- **InfluxDB + Grafana**: `data/influx.py` exists and `requirements.txt`
  already stubs `influxdb-client` — enable it for time-series history and
  season-over-season comparisons.
- **Kriging heatmaps**: `pykrige` path already coded in `data/heatmap.py`;
  install the optional dep for smoother soil maps.
- **Prescription-map export to ISOXML** — DONE (§0): `to_isoxml()` emits an
  ISO 11783-10 TASKDATA set (v4.2, GridType 2) for commercial tractor
  terminals. Shapefile export remains optional future work.
- **Yield/health trend model**: the per-plant observation DB (`plant_db.py`)
  accumulates exactly the longitudinal data needed for a simple
  disease-progression / hotspot-prediction model later.

## 8. Training pipeline & MLOps (P1–P2)

- **Active-learning loop** — capture side DONE (§0): `pi/ai/frame_capture.py`
  saves low-confidence + periodic frames with JSON sidecars into `captures/`.
  Remaining: weekly re-annotate (Roboflow/CVAT) → fine-tune → redeploy. This
  is how field accuracy actually gets good.
- **Model versioning & OTA** — DONE (§0): `pi/ai/model_ota.py`
  (make-manifest / update / rollback) + weekly `agrobot-model-ota.timer`;
  release workflow in `deploy/README.md` §Model OTA.
- **On-device benchmark** — DONE (§0): `python pi/ai/benchmark.py` measures
  mean/p95 latency + FPS per loaded backend and appends to `benchmarks.jsonl`.
  Run it after every model/hardware change.
- **Eval set (P1)**: hold out a fixed local-field test set; every retrain
  reports mAP/accuracy against it before deployment.

## 9. Farmer-facing intelligence (P2–P3)

- **Two-way Telegram control** — DONE (§0): /stop /go /status /photo /summary
  with a chat-ID allowlist (fail closed), stdlib-only long polling.
- **Dashboard upgrades (P2)**: live detection overlay stream, plant-DB map
  layer (folium/pydeck already in requirements), mission progress.
- **LLM agronomy assistant (P3)**: turn detections + soil trends into plain-
  language, local-language advice ("Zone 3 nitrogen low + early blight on 4
  plants → recommended action…"). Options: cloud API (e.g. Anthropic Claude)
  when connectivity allows, or a small on-device VLM (SmolVLM / Moondream
  class models run on Pi 5-grade hardware in 2026) for offline field Q&A.
- **Voice interface in local languages (P3)**: whisper.cpp-class STT on Pi 5.

## 10. Platform, reliability & security (P1–P2)

- **Enable MQTT TLS + auth in deployment** — DONE (§0): `deploy/mosquitto.conf`
  + `deploy/gen_certs.sh`; bring-up order in `deploy/README.md`.
- **ESP32 secure boot + signed OTA** (P2): documented in `SECURITY.md`;
  implement before any field fleet.
- **Watchdogs** — DONE (§0): systemd `Restart=always` in all units + hardware
  watchdog via `harden_pi.sh --watchdog`; ESP32 already has the link-heartbeat
  dead-man.
- **CI** (P2): GitHub Actions — py_compile/pytest for `pi/`, PlatformIO build
  for `firmware/` (use `py -3.14 -m platformio` locally on Windows).
- **Unit tests** — DONE (§0): `pi/tests/` covers the pure-math core with 47
  tests (`py -3.14 -m pytest pi/tests`). Extend alongside new features.

---

## Priority summary

| # | Item | Cost | Impact |
|---|------|------|--------|
| P0 | Train + deploy the 3 models (Colab) | free, ~half a day | AI goes from inert to working |
| P0 | ~~Wire undistort/ToF into main loop~~ DONE · camera calibration remains | free, hours | accuracy of every downstream feature |
| P1 | YOLO26n retrain + QAT (notebooks default to YOLO26n; QAT/eval stage now in the notebooks — just re-run on Colab) | free, hours | +speed +mAP on same hardware |
| P1 | ~~Active-learning capture loop~~ DONE · fixed eval set remains | free, ~1 day | the path to real field accuracy |
| P1 | RTK GNSS (ZED-F9P) — EKF fusion already wired, just lower `GPS_VAR_M2` | $250–450 | 1 m → 1 cm; per-plant precision |
| P1 | ~~MQTT TLS on, watchdogs, pytest suite~~ DONE (117 tests; `deploy/README.md`) | free | reliability/security floor |
| P2 | ~~Pi 5 + AI HAT+ (Hailo-8 26 TOPS)~~ SELECTED — `hailo_backend.py` wired, docs/BOM updated; drop in `.hef` after Colab export | ~$190 + Pi 5 | 5–10× inference headroom, seg models |
| P2 | OAK-D depth / IMX500 smart cam / NDVI NoIR | $30–150 each | avoidance, aim depth, stress maps |
| P2 | Weed segmentation + size-scaled dosing | free, days | less chemical, better kills |
| P2 | Pathway-native pipeline, Influx+Grafana · ~~ISOXML export, model OTA~~ DONE | free, days | pro-grade data story |
| P3 | Laser/mechanical weeding, Nav2, fleet, LLM/voice advisor | varies | the moonshots |

## Sources

- [Ultralytics YOLO26 announcement](https://www.ultralytics.com/news/ultralytics-redefines-state-of-the-art-vision-ai-with-yolo26) · [YOLO26 vs YOLO11](https://docs.ultralytics.com/compare/yolo26-vs-yolo11) · [Raspberry Pi guide/benchmarks](https://docs.ultralytics.com/guides/raspberry-pi) · [Datature YOLO26 review](https://datature.io/blog/yolo26-the-edge-first-evolution-of-real-time-object-detection) · [Roboflow YOLO26 / RF-DETR](https://blog.roboflow.com/yolo26/)
- [Hailo-8 vs Coral (Frigate, 2026)](https://botmonster.com/smart-home/hailo-8-vs-coral-tpu-frigate-nvr-comparison/) · [Seeed: AI Kit vs Coral](https://www.seeedstudio.com/blog/2024/07/16/raspberry-pi-ai-kit-vs-coral-usb-accelerator-vs-coral-m-2-accelerator-with-dual-edge-tpu/) · [Jeff Geerling AI Kit tests](https://www.jeffgeerling.com/blog/2024/testing-raspberry-pis-ai-kit-13-tops-70/) · [AI HAT+ getting started](https://buyzero.de/en/blogs/news/getting-started-with-the-new-ai-hat-for-the-raspberry-pi-5)
- [Raspberry Pi AI Camera (IMX500)](https://www.raspberrypi.com/products/ai-camera/) · [AI Camera docs](https://www.raspberrypi.com/documentation/accessories/ai-camera.html)
- [MDPI systematic review: weed/pest robots (Feb 2026)](https://doi.org/10.3390/make8020051) · [Laser weeding review, Smart Agriculture 2025](https://www.sciopen.com/article/10.12133/j.smartag.SA202410031) · [LiteWeed edge laser platform](https://www.sciencedirect.com/science/article/pii/S2772375526005654) · [Robotic weeding sensing review](https://pmc.ncbi.nlm.nih.gov/articles/PMC11510896/) · [Shadow-bias weed detection](https://arxiv.org/pdf/2508.19511) · [NC State: AI robotic weeders](https://content.ces.ncsu.edu/artificial-intelligence-ai-enabled-robotic-weeders-in-precision-agriculture) · [FarmDroid](https://farmdroid.com/)
- [u-blox ZED-F9P](https://www.u-blox.com/en/product/zed-f9p-module) · [ArduSimple simpleRTK2B](https://www.ardusimple.com/product/simplertk2b/) · [Waveshare ZED-F9P Pi HAT](https://www.waveshare.com/zed-f9p-gps-rtk-hat.htm) · [DIY RTK guide](https://github.com/hcwinsemius/RTK_GNSS)
- [Low-cost NDVI imaging system (Plant Methods 2023)](https://plantmethods.biomedcentral.com/articles/10.1186/s13007-023-00981-8) · [OAK-D Lite on Pi](https://core-electronics.com.au/guides/oak-d-lite-raspberry-pi/)
