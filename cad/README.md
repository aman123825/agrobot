# AgriRover — Fusion 360 Prototype (CAD)

A script that **programmatically builds the entire AgriRover rover as a to-scale
3D prototype inside Autodesk Fusion 360**. Every component from
[`../docs/mechanical-layout.md`](../docs/mechanical-layout.md) is created as its
own named, colour-coded Fusion component, placed at its real footprint and
position on the correct deck.

> This is the *digital twin* of the physical build in
> [`../BUILD.md`](../BUILD.md). The mechanical layout doc is the single source of
> truth for footprints and positions; this script draws exactly that.

```
cad/
└── AgriRoverPrototype/
    ├── AgriRoverPrototype.py         # the generator script
    └── AgriRoverPrototype.manifest   # Fusion script descriptor
```

---

## What it builds

A double-decker chassis (**320 × 450 mm**) with **58 components** organised into
an assembly tree that mirrors the physical rover:

| Browser group | Contents |
|---|---|
| `00 Chassis & Structure` | soil plane, lower + upper acrylic deck plates, 4 inter-deck standoffs, 4 mast posts, reflective sun canopy |
| `01 Drivetrain` | 4 × 12 V gear motors (cylinders along the axle) + 4 × 65 mm rubber wheels |
| `02 Underside` | front/rear HC-SR04, cutter/weeder, 150 N linear actuator, NPK probe (spike into the soil) |
| `03 Lower Deck` | power (rocker, XT60, fuse, buck, INA219, bus, power bank, LiPo), fluid (pump, 500 ml tank, float) and drive (2-ch relay, ACS712, 2 × BTS7960) |
| `04 Upper Deck` | compute (ESP32, ESP32-CAM, Pi 4, Coral, fan, LoRa), sensors (I²C IMU/ADC/GPIO/ToF board, MAX485) and UI (OLED, mode switch, buttons, E-STOP) |
| `05 Top & Mast` | GPS, LoRa antenna, ultrasonic sweep servo, Pi camera, DHT22, rain sensor |

Components are coloured by zone using the same legend as
[`../docs/chassis-layout.svg`](../docs/chassis-layout.svg): power = tan,
drive = red, fluid = light-blue, compute = blue, sensor = green, UI = yellow,
mechanical = grey.

---

## How to run it in Fusion 360

1. Open **Fusion 360**.
2. Go to the **Utilities** tab → **ADD-INS** → **Scripts and Add-Ins…**
   (or press **Shift + S**).
3. On the **Scripts** tab, click the green **“+”** next to *My Scripts* →
   **“Add existing script”** (some versions: the small **+** / folder icon).
4. Browse to this repo and select the folder:
   `cad/AgriRoverPrototype`
   Fusion picks up `AgriRoverPrototype.py` via the `.manifest`.
5. Select **AgriRoverPrototype** in the list and click **Run**.

The script opens a **new, empty design** (so it never disturbs anything you
already have open), builds the rover, fits the view, and pops a summary dialog:

```
AgriRover prototype built.

Components created : 58
Chassis            : 320 x 450 mm (double-decker)
Decks              : underside / lower / upper / top-mast
```

Rotate/orbit to inspect. The full assembly is ~**320 × 450 mm** footprint and
~**327 mm** tall (ground to antenna tip).

> **Tip:** to re-run after editing, just press **Run** again — it creates a
> fresh document each time. Close the previous one without saving if you don’t
> need it.

---

## Coordinate system

Matches the docs exactly:

| Axis | Meaning | Range |
|---|---|---|
| Origin | chassis **front-left corner at ground level** | (0,0,0) |
| **+X** | across the chassis, to the **right** | 0 → 320 mm (width) |
| **+Y** | from the **front** toward the **rear** | 0 → 450 mm (length) |
| **+Z** | up | ground → mast |

The rover **front** (drive + camera direction) is the **y = 0** edge.

Vertical stack (mm from ground):

```
  257  ┌ sun canopy ┐   ← top & mast components sit here
       │  mast posts │
  162  ├ upper deck ─┤   ← compute / sensors / UI
       │  standoffs  │
   68  ├ lower deck ─┤   ← power / drive / fluid
   64  └────────────┘    (underside components hang below)
   38          ● motor centre-line
    0  ══ ground ══ (wheels Ø65 span 0–65)   NPK probe dips to −30
```

Deck spacing is drawn slightly larger than the “~60–70 mm standoffs” note in the
layout doc so tall lower-deck parts (the 500 ml tank) clear the upper deck in the
model. Edit the `Z_*` constants at the top of the script to match your exact
standoff stack.

---

## Customising

All geometry is data-driven from the `PARTS` list near the top of
`AgriRoverPrototype.py`. Each entry is:

```python
dict(n="Raspberry Pi 4", zone='compute', deck='upper',
     x=120, y=18, w=85, l=56, h=25)
#    name              colour        which deck
#    x,y = front-left corner (mm)   w,l = footprint (mm)   h = height (mm)
```

- Change a footprint or position → edit `x, y, w, l`.
- Change a part’s height → edit `h` (heights are model estimates from typical
  real part sizes; footprints/positions come straight from the layout doc).
- Toggle behaviour with the flags at the top: `ADD_APPEARANCES`, `ADD_GROUND`,
  `ADD_WHEELS`, `SHOW_SUMMARY`.
- Special shapes: `'motory'` (cylinder along the axle), `'probe'` (vertical
  spike into the soil), `'postz'` (vertical rod, e.g. the antenna). Everything
  else is a box at its footprint.

---

## Making it “move” (motion study)

The model is built **motion-ready**: motors and wheels are separate components,
so you can add joints and animate the drivetrain.

1. **ASSEMBLE → Joint** (press **J**).
2. Pick a **Revolute** joint between a `Wheel *` component and the adjacent
   `Motor *` (or the chassis). Choose the axle axis as the rotation axis.
3. Repeat for all four wheels.
4. **DESIGN → Motion Study** (or right-click a joint → **Animate Joint**) to spin
   the wheels / sweep the ultrasonic servo.

> Joints are intentionally **not** auto-created by the script — auto-joints are
> fragile across Fusion versions and would risk aborting the whole build. The
> component split makes adding them a 2-minute manual step.

---

## Exporting

- **STEP / SAT** (share with any CAD): **File → Export**, choose `.step`.
- **STL / 3MF** (3-D print the printed parts — motor mounts, brackets):
  right-click a component → **Save as Mesh**.
- **Screenshots / turntable**: **File → Capture Image**, or use the **Render**
  workspace for a presentation-quality image for the pitch deck.

---

## Notes & limitations

- Components are **massing primitives** (boxes/cylinders at true footprints), not
  detailed part models — the goal is an accurate spatial + assembly prototype of
  the whole rover, fast to regenerate, matching the BOM and layout 1:1.
- Requires the Fusion 360 desktop app (the `adsk` API only exists inside Fusion);
  the script cannot run headless. Its Python is otherwise standard and has been
  syntax-checked and logic-verified against a mock of the `adsk` API.
- Firmware/software for the rover live in [`../firmware`](../firmware) and
  [`../pi`](../pi); this directory is only the mechanical/CAD prototype.
