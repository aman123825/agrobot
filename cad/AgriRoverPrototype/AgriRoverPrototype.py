# -*- coding: utf-8 -*-
"""
AgriRover - Fusion 360 prototype generator
===========================================

Programmatically builds a full, to-scale 3D prototype of the AgriRover
autonomous agricultural rover directly inside Autodesk Fusion 360.

Every component from ``docs/mechanical-layout.md`` is created as its own named,
colour-coded Fusion component, placed at its real footprint and position on the
correct deck of the double-decker chassis. The result is a browser tree that
mirrors the physical build:

    AgriRover Prototype
    |- 00 Chassis & Structure   (deck plates, standoffs, sun canopy, soil)
    |- 01 Drivetrain            (4 gear motors + 4 wheels)
    |- 02 Underside             (ultrasonics, cutter, actuator, NPK probe)
    |- 03 Lower Deck            (power / drive / fluid)
    |- 04 Upper Deck            (compute / sensors / UI)
    |- 05 Top & Mast            (GPS, camera, antenna, weather sensors)

Coordinate system (matches docs/mechanical-layout.md + chassis-layout.svg):
    * Origin (0,0,0) = chassis FRONT-LEFT corner at ground level.
    * +X = across the chassis to the RIGHT   (width  = 320 mm)
    * +Y = from FRONT toward the REAR         (length = 450 mm)
    * +Z = up
    * FRONT of the rover (drive / camera direction) is the y = 0 edge.

All layout numbers below are in MILLIMETRES (to match the docs). The Fusion API
works in centimetres, so every value is multiplied by ``MM`` (= 0.1) at the
point it is handed to the API.

HOW TO RUN
    Utilities tab -> ADD-INS -> Scripts and Add-Ins -> (My Scripts) green "+"
    -> pick this folder -> select "AgriRoverPrototype" -> Run.
    See cad/README.md for full instructions.

This script is self-contained and read-only with respect to the rest of the
repo - it just draws geometry. It creates a NEW Fusion document, so it never
disturbs a design you already have open.
"""

import adsk.core
import adsk.fusion
import traceback
import math

# --------------------------------------------------------------------------- #
#  Options
# --------------------------------------------------------------------------- #
ADD_APPEARANCES = True   # colour every component by zone (set False if slow)
ADD_GROUND      = True   # draw a soil plane under the rover for context
ADD_WHEELS      = True   # draw the 4 rubber wheels
SHOW_SUMMARY    = True    # pop a message box with the build report at the end

# --------------------------------------------------------------------------- #
#  Units + vertical stack (all millimetres)
# --------------------------------------------------------------------------- #
MM = 0.1  # millimetre -> centimetre (Fusion API is in cm)

CHASSIS_W = 320.0   # +X extent
CHASSIS_L = 450.0   # +Y extent

WHEEL_DIA   = 65.0
WHEEL_WIDTH = 27.0
WHEEL_R     = WHEEL_DIA / 2.0

MOTOR_Z     = 38.0   # motor centre-line height (couples to wheel centre)

# Deck plate top/bottom faces (Z, mm from ground)
Z_LOWER_BOT   = 64.0
Z_LOWER_TOP   = 68.0    # lower-deck components sit on this face
PLATE_T       = 4.0     # acrylic deck thickness
Z_UPPER_BOT   = 158.0
Z_UPPER_TOP   = 162.0   # upper-deck components sit on this face
CANOPY_T      = 3.0
Z_CANOPY_BOT  = 254.0
Z_CANOPY_TOP  = 257.0   # mast / top components sit on this face

# --------------------------------------------------------------------------- #
#  Zone -> RGB colour (matches the legend in docs/chassis-layout.svg)
# --------------------------------------------------------------------------- #
COLORS = {
    'power':   (246, 194, 122),   # tan/orange
    'drive':   (244, 140, 150),   # red/pink
    'fluid':   (154, 208, 236),   # light blue
    'compute': (144, 202, 249),   # blue
    'sensor':  (165, 214, 167),   # green
    'ui':      (255, 213,  79),   # yellow
    'mech':    (207, 216, 220),   # grey
    # structural / drivetrain
    'acrylic': (205, 216, 222),   # deck plates
    'canopy':  (240, 240, 240),   # reflective sun canopy
    'soil':    (120,  85,  55),   # ground plane
    'wheel':   ( 35,  35,  38),   # rubber tyre
    'motor':   (210,  70,  80),   # gear motor
    'metal':   (175, 178, 182),   # standoffs / mast posts
}

# --------------------------------------------------------------------------- #
#  Component catalogue  (from docs/mechanical-layout.md)
#  Each entry: name, zone, deck, x, y, w(=X size), l(=Y size), h(=Z size)
#  Optional 'shape': 'box' (default) | 'motory' | 'probe' | 'postz'
#  x,y = front-left corner of the footprint (mm from chassis front-left).
# --------------------------------------------------------------------------- #
PARTS = [
    # ---- 1. Underside (ground-facing mechanicals) --------------------------
    dict(n="HC-SR04 Front",        zone='mech',    deck='under', x=137, y=4,   w=45, l=20, h=15),
    dict(n="HC-SR04 Rear",         zone='mech',    deck='under', x=137, y=426, w=45, l=20, h=15),
    dict(n="Cutter-Weeder",        zone='mech',    deck='under', x=125, y=120, w=70, l=60, h=54),
    dict(n="Linear Actuator 150N", zone='drive',   deck='under', x=140, y=300, w=40, l=40, h=60),
    dict(n="NPK Probe Head",       zone='sensor',  deck='under', x=137, y=345, w=45, l=45, h=94, shape='probe'),
    # motors (drawn as cylinders lying along Y, hanging under the lower deck)
    dict(n="Motor FL",             zone='drive',   deck='drive', x=16,  y=70,  w=37, l=70, h=37, shape='motory'),
    dict(n="Motor FR",             zone='drive',   deck='drive', x=267, y=70,  w=37, l=70, h=37, shape='motory'),
    dict(n="Motor RL +Enc",        zone='drive',   deck='drive', x=16,  y=310, w=37, l=70, h=37, shape='motory'),
    dict(n="Motor RR +Enc",        zone='drive',   deck='drive', x=267, y=310, w=37, l=70, h=37, shape='motory'),

    # ---- 2. Lower deck (power / drive / fluid) -----------------------------
    dict(n="Rocker Switch",        zone='power',   deck='lower', x=10,  y=8,   w=20, l=20, h=15),
    dict(n="XT60 Connector",       zone='power',   deck='lower', x=34,  y=10,  w=22, l=16, h=12),
    dict(n="Fuse 30A",             zone='power',   deck='lower', x=10,  y=32,  w=30, l=16, h=12),
    dict(n="LM2596 Buck",          zone='power',   deck='lower', x=10,  y=54,  w=43, l=21, h=15),
    dict(n="INA219",               zone='power',   deck='lower', x=60,  y=54,  w=26, l=18, h=10),
    dict(n="Screw Bus",            zone='power',   deck='lower', x=10,  y=80,  w=42, l=18, h=12),
    dict(n="Pump 12V",             zone='fluid',   deck='lower', x=105, y=18,  w=60, l=40, h=40),
    dict(n="Fertilizer Tank 500ml",zone='fluid',   deck='lower', x=178, y=12,  w=90, l=70, h=80),
    dict(n="Float Sensor",         zone='fluid',   deck='lower', x=250, y=18,  w=16, l=16, h=30),
    dict(n="Power Bank 10Ah",      zone='power',   deck='lower', x=10,  y=150, w=70, l=140,h=22),
    dict(n="LiPo 3S 2200mAh",      zone='power',   deck='lower', x=150, y=165, w=34, l=105,h=24),
    dict(n="2ch Relay",            zone='drive',   deck='lower', x=250, y=150, w=51, l=39, h=18),
    dict(n="ACS712 x2",            zone='drive',   deck='lower', x=250, y=300, w=34, l=22, h=12),
    dict(n="BTS7960 #1",           zone='drive',   deck='lower', x=95,  y=372, w=50, l=50, h=22),
    dict(n="BTS7960 #2",           zone='drive',   deck='lower', x=175, y=372, w=50, l=50, h=22),

    # ---- 3. Upper deck (compute / sensors / UI) ----------------------------
    dict(n="ESP32 DevKit V1",      zone='compute', deck='upper', x=24,  y=24,  w=55, l=28, h=13),
    dict(n="ESP32-CAM",            zone='compute', deck='upper', x=24,  y=66,  w=40, l=27, h=12),
    dict(n="Raspberry Pi 4",       zone='compute', deck='upper', x=120, y=18,  w=85, l=56, h=25),
    dict(n="Coral TPU",            zone='compute', deck='upper', x=218, y=20,  w=65, l=30, h=10),
    dict(n="30mm Fan",             zone='compute', deck='upper', x=148, y=80,  w=30, l=30, h=12),
    dict(n="I2C Board (IMU/ADC/GPIO/ToF)", zone='sensor', deck='upper', x=120, y=150, w=80, l=58, h=22),
    dict(n="MAX485",               zone='sensor',  deck='upper', x=214, y=160, w=22, l=15, h=12),
    dict(n="LoRa SX1276",          zone='compute', deck='upper', x=246, y=160, w=18, l=16, h=12),
    dict(n="OLED 0.96in",          zone='ui',      deck='upper', x=18,  y=378, w=27, l=27, h=8),
    dict(n="Mode Switch",          zone='ui',      deck='upper', x=66,  y=382, w=20, l=20, h=18),
    dict(n="Buttons x4",           zone='ui',      deck='upper', x=100, y=386, w=50, l=14, h=10),
    dict(n="E-STOP",               zone='ui',      deck='upper', x=180, y=378, w=28, l=28, h=30),

    # ---- 4. Top & mast (above the upper deck) ------------------------------
    dict(n="GPS Neo-6M",           zone='sensor',  deck='mast',  x=140, y=12,  w=25, l=25, h=12),
    dict(n="LoRa Antenna",         zone='compute', deck='mast',  x=288, y=12,  w=10, l=70, h=70, shape='postz'),
    dict(n="US Sweep SG90",        zone='mech',    deck='mast',  x=150, y=78,  w=23, l=12, h=22),
    dict(n="Pi Camera + 160 Lens", zone='sensor',  deck='mast',  x=147, y=118, w=26, l=24, h=16),
    dict(n="DHT22",                zone='sensor',  deck='mast',  x=40,  y=60,  w=15, l=28, h=12),
    dict(n="Rain Sensor",          zone='sensor',  deck='mast',  x=240, y=120, w=40, l=30, h=6),
]

# 4 rubber wheels, paired with the 4 motors (outboard of the chassis sides).
#   name, x-start (mm), y-centre (mm)
WHEELS = [
    ("Wheel FL", -WHEEL_WIDTH,      105.0),
    ("Wheel RL", -WHEEL_WIDTH,      345.0),
    ("Wheel FR",  CHASSIS_W,        105.0),
    ("Wheel RR",  CHASSIS_W,        345.0),
]

# M3 standoff / mast post corners (inset from the chassis corners).
CORNERS = [(12.0, 12.0), (CHASSIS_W - 12.0, 12.0),
           (12.0, CHASSIS_L - 12.0), (CHASSIS_W - 12.0, CHASSIS_L - 12.0)]

# --------------------------------------------------------------------------- #
#  Appearance helper (robust: never aborts the build if colouring fails)
# --------------------------------------------------------------------------- #
_APPEARANCE_CACHE = {}


def get_appearance(app, design, zone):
    """Return (and cache) a coloured Appearance for a zone, or None on failure."""
    if not ADD_APPEARANCES:
        return None
    if zone in _APPEARANCE_CACHE:
        return _APPEARANCE_CACHE[zone]

    rgb = COLORS.get(zone, (200, 200, 200))
    appearance = None
    try:
        appearances = design.appearances
        name = "AgriRover_%s" % zone
        existing = appearances.itemByName(name)
        if existing:
            _APPEARANCE_CACHE[zone] = existing
            return existing

        lib = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
        base = None
        for cand in ('Plastic - Matte (White)',
                     'Powder Coat (White)',
                     'Paint - Enamel Glossy (White)',
                     'Plastic - Matte (Yellow)'):
            base = lib.appearances.itemByName(cand)
            if base:
                break
        if base is None and lib.appearances.count > 0:
            base = lib.appearances.item(0)

        new_appear = appearances.addByCopy(base, name)

        # Find the first colour property on the appearance and set our RGB.
        props = new_appear.appearanceProperties
        for i in range(props.count):
            cp = adsk.core.ColorProperty.cast(props.item(i))
            if cp:
                cp.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                break
        appearance = new_appear
    except Exception:
        appearance = None

    _APPEARANCE_CACHE[zone] = appearance
    return appearance


def paint(body, appearance):
    if appearance:
        try:
            body.appearance = appearance
        except Exception:
            pass


# --------------------------------------------------------------------------- #
#  Geometry primitives (built in each component's LOCAL frame, on XY, +Z)
# --------------------------------------------------------------------------- #
def _extrude(comp, profile, length_mm):
    extrudes = comp.features.extrudeFeatures
    dist = adsk.core.ValueInput.createByReal(length_mm * MM)
    ext_in = extrudes.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext_in.setDistanceExtent(False, dist)
    ext = extrudes.add(ext_in)
    return ext.bodies.item(0)


def make_box(comp, w, l, h):
    """Box with its min corner at the component origin, extruded +Z."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(0, 0, 0),
        adsk.core.Point3D.create(w * MM, l * MM, 0))
    return _extrude(comp, sk.profiles.item(0), h)


def make_cyl(comp, radius, length):
    """Cylinder centred on the component origin (bottom face), extruded +Z."""
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), radius * MM)
    return _extrude(comp, sk.profiles.item(0), length)


# --------------------------------------------------------------------------- #
#  Placement helpers
# --------------------------------------------------------------------------- #
def _transform(deg, axis, tx, ty, tz):
    """Rotate about the local origin by `deg` around `axis`, then translate (mm)."""
    m = adsk.core.Matrix3D.create()
    if deg:
        m.setToRotation(math.radians(deg), axis, adsk.core.Point3D.create(0, 0, 0))
    m.translation = adsk.core.Vector3D.create(tx * MM, ty * MM, tz * MM)
    return m


def new_component(parent, name, transform):
    occ = parent.occurrences.addNewComponent(transform)
    occ.component.name = name
    return occ.component


AX_X = adsk.core.Vector3D.create(1, 0, 0)
AX_Y = adsk.core.Vector3D.create(0, 1, 0)


def deck_base(part):
    """Bottom Z (mm) of a component from its deck."""
    shape = part.get('shape', 'box')
    if shape == 'probe':
        return -30.0                       # NPK spike reaches into the soil
    d = part['deck']
    if d == 'under':
        return Z_LOWER_BOT - part['h']     # hangs beneath the lower deck
    if d == 'lower':
        return Z_LOWER_TOP
    if d == 'upper':
        return Z_UPPER_TOP
    if d == 'mast':
        return Z_CANOPY_TOP
    return 0.0


def build_part(app, design, group, part):
    """Create one catalogue component inside its deck group."""
    shape = part.get('shape', 'box')
    x, y = part['x'], part['y']
    w, l, h = part['w'], part['l'], part['h']
    appearance = get_appearance(app, design, part['zone'])

    if shape == 'motory':
        # gear motor: cylinder lying along +Y, centre-line at Z=MOTOR_Z
        r = w / 2.0
        m = _transform(-90, AX_X, x + w / 2.0, y, MOTOR_Z)
        comp = new_component(group, part['n'], m)
        body = make_cyl(comp, r, l)
        paint(body, get_appearance(app, design, 'motor'))
        return comp

    if shape == 'probe':
        # NPK spike: vertical cylinder from soil up to the underside
        cx, cy = x + w / 2.0, y + l / 2.0
        m = _transform(0, AX_X, cx, cy, deck_base(part))
        comp = new_component(group, part['n'], m)
        body = make_cyl(comp, 8.0, h)
        paint(body, appearance)
        return comp

    if shape == 'postz':
        # vertical rod (e.g. LoRa antenna) standing on the canopy
        cx, cy = x + w / 2.0, y + l / 2.0
        r = min(w, l) / 2.0
        m = _transform(0, AX_X, cx, cy, deck_base(part))
        comp = new_component(group, part['n'], m)
        body = make_cyl(comp, r, h)
        paint(body, appearance)
        return comp

    # default: box on its deck
    m = _transform(0, AX_X, x, y, deck_base(part))
    comp = new_component(group, part['n'], m)
    body = make_box(comp, w, l, h)
    paint(body, appearance)
    return comp


def build_wheel(app, design, group, name, x_start, y_centre):
    """Rubber wheel: cylinder whose axis lies along +X, outboard of the chassis."""
    m = _transform(90, AX_Y, x_start, y_centre, WHEEL_R)
    comp = new_component(group, name, m)
    body = make_cyl(comp, WHEEL_R, WHEEL_WIDTH)
    paint(body, get_appearance(app, design, 'wheel'))
    return comp


def build_plate(app, design, group, name, z_bot, thick, zone):
    m = _transform(0, AX_X, 0, 0, z_bot)
    comp = new_component(group, name, m)
    body = make_box(comp, CHASSIS_W, CHASSIS_L, thick)
    paint(body, get_appearance(app, design, zone))
    return comp


def build_post(app, design, group, name, cx, cy, z_bot, length, radius, zone):
    m = _transform(0, AX_X, cx, cy, z_bot)
    comp = new_component(group, name, m)
    body = make_cyl(comp, radius, length)
    paint(body, get_appearance(app, design, zone))
    return comp


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Fresh design document so we never touch the user's open work.
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)

        # Direct modelling (no timeline) keeps ~60 bodies fast to generate.
        design.designType = adsk.fusion.DesignTypes.DirectDesignType
        try:
            design.fusionUnitsManager.distanceDisplayUnits = \
                adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        except Exception:
            pass

        root = design.rootComponent
        try:
            root.name = "AgriRover Prototype"
        except Exception:
            pass  # root component name is read-only in some versions

        # ---- assembly groups (browser tree) --------------------------------
        ident = adsk.core.Matrix3D.create()
        g_struct = new_component(root, "00 Chassis & Structure", ident)
        g_drive  = new_component(root, "01 Drivetrain",          ident)
        g_under  = new_component(root, "02 Underside",           ident)
        g_lower  = new_component(root, "03 Lower Deck",          ident)
        g_upper  = new_component(root, "04 Upper Deck",          ident)
        g_mast   = new_component(root, "05 Top & Mast",          ident)

        group_by_deck = {
            'under': g_under, 'lower': g_lower,
            'upper': g_upper, 'mast': g_mast, 'drive': g_drive,
        }

        built = 0
        errors = []

        # ---- structure: soil, deck plates, standoffs, sun canopy -----------
        if ADD_GROUND:
            m = _transform(0, AX_X, -60, -60, -2)
            comp = new_component(g_struct, "Soil", m)
            paint(make_box(comp, CHASSIS_W + 120, CHASSIS_L + 120, 2),
                  get_appearance(app, design, 'soil'))
            built += 1

        build_plate(app, design, g_struct, "Lower Deck Plate", Z_LOWER_BOT, PLATE_T, 'acrylic'); built += 1
        build_plate(app, design, g_struct, "Upper Deck Plate", Z_UPPER_BOT, PLATE_T, 'acrylic'); built += 1
        build_plate(app, design, g_struct, "Sun Canopy",       Z_CANOPY_BOT, CANOPY_T, 'canopy'); built += 1

        for i, (cx, cy) in enumerate(CORNERS, 1):
            build_post(app, design, g_struct, "Standoff L%d" % i, cx, cy,
                       Z_LOWER_TOP, Z_UPPER_BOT - Z_LOWER_TOP, 5.0, 'metal'); built += 1
            build_post(app, design, g_struct, "Mast Post %d" % i, cx, cy,
                       Z_UPPER_TOP, Z_CANOPY_BOT - Z_UPPER_TOP, 5.0, 'metal'); built += 1

        # ---- catalogue components ------------------------------------------
        for part in PARTS:
            grp = group_by_deck[part['deck']]
            try:
                build_part(app, design, grp, part)
                built += 1
            except Exception as ex:
                errors.append("%s: %s" % (part['n'], ex))

        # ---- wheels --------------------------------------------------------
        if ADD_WHEELS:
            for name, xs, yc in WHEELS:
                try:
                    build_wheel(app, design, g_drive, name, xs, yc)
                    built += 1
                except Exception as ex:
                    errors.append("%s: %s" % (name, ex))

        # ---- fit the view --------------------------------------------------
        try:
            app.activeViewport.fit()
            cam = app.activeViewport.camera
            cam.isFitView = True
            app.activeViewport.camera = cam
        except Exception:
            pass

        if SHOW_SUMMARY and ui:
            msg = ("AgriRover prototype built.\n\n"
                   "Components created : %d\n"
                   "Chassis            : %.0f x %.0f mm (double-decker)\n"
                   "Decks              : underside / lower / upper / top-mast\n"
                   % (built, CHASSIS_W, CHASSIS_L))
            if errors:
                msg += "\nSkipped (%d):\n - %s" % (len(errors), "\n - ".join(errors))
            ui.messageBox(msg, "AgriRover Prototype")

    except Exception:
        if ui:
            ui.messageBox('AgriRover script failed:\n{}'.format(traceback.format_exc()),
                          "AgriRover Prototype")
