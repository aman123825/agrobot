"""ISO 11783-10 (ISOXML) task-file exporter for prescription maps.

Turns an AgriRover prescription grid into a TASKDATA/ folder (TASKDATA.XML +
grid binary, optionally zipped) that commercial tractor terminals and FMIS
packages can import for variable-rate application.

Spec conventions implemented (chosen to match the common denominator of
open-source ISOXML implementations such as the isoxml JS/Python libraries,
the QGIS ISOXML plugins and AgOpenGPS-adjacent tooling; every assumption is
listed here so it can be audited against ISO 11783-10):

* Version: root ``<ISO11783_TaskData VersionMajor="4" VersionMinor="2">``.
  Version 4 (2nd edition, 2015) is what current terminals and FMIS emit; the
  minimal element subset used here (TSK, PFD, PLN, LSG, PNT, GRD, TZN, PDV,
  PDT) is unchanged between version 3 and 4, so v4/2 is the safer choice for
  modern terminals while still parsing on older ones (we use no v4-only
  features).  ``DataTransferOrigin="1"`` marks the file as FMIS-created.
* Attribute names: ISO 11783-10 XML uses single-letter attribute codes on
  all elements except the root.  The letters emitted here map to:
  PDT  A=ProductId B=ProductDesignator;
  PFD  A=PartfieldId C=PartfieldDesignator D=PartfieldArea (m^2, integer);
  PLN  A=PolygonType (1 = partfield boundary);
  LSG  A=LineStringType (1 = polygon exterior);
  PNT  A=PointType (2 = "other", the usual choice for boundary vertices)
       C=PointNorth (lat, decimal degrees) D=PointEast (lon);
  TSK  A=TaskId B=TaskDesignator E=PartfieldIdRef G=TaskStatus (1 = planned);
  TZN  A=TreatmentZoneCode B=TreatmentZoneDesignator;
  PDV  A=ProcessDataDDI (4-digit hex) B=ProcessDataValue C=ProductIdRef;
  GRD  A=GridMinimumNorthPosition B=GridMinimumEastPosition
       C=GridCellNorthSize D=GridCellEastSize (both decimal degrees)
       E=GridMaximumColumn F=GridMaximumRow G=Filename H=FileLength
       I=GridType J=TreatmentZoneCode.
* Grid: GridType 2 ("one TZN, values in the binary") — the grid binary holds
  one little-endian signed 32-bit integer per cell, and ``GRD J`` points at a
  single ``<TZN>`` whose ``<PDV>`` declares the DDI those integers belong to.
  Cell order is row-major starting at the grid minimum (south-west) corner:
  rows run south -> north, columns within a row run west -> east.  This is
  the ISO 11783-10 grid convention shared by all implementations checked.
* DDI: the PDV is emitted with ``A="0006"`` (project-pinned "setpoint
  application rate as volume per area, mm3/m2").  Note for auditors: the ISO
  11783-11 DDI database lists 0x0001 as Setpoint Volume Per Area Application
  Rate [mm3/m2] and 0x0006 as Setpoint Mass Per Area Application Rate
  [mg/m2]; both use the same x100 factor from field units (1 L/ha = 100
  mm3/m2 and 1 kg/ha = 100 mg/m2), so the encoded cell values are identical
  either way.  DDI 0006 is used here as specified for this project.
* Units: input rates default to L/ha and are converted with
  1 L/ha = 100 mm3/m2 (1 L = 1e6 mm3, 1 ha = 1e4 m2).  Pass
  ``rate_unit_l_per_ha=False`` if values are already in mm3/m2.  Cell values
  are rounded to int, negatives clamped to 0, and capped at 2^31 - 1 so they
  always fit the int32 cell; cells with no data are written as 0.
* Boundary: the partfield ``<PLN>`` is the grid's outer bounding rectangle
  (cell edges, not cell centres) as an explicitly closed ring of 5 ``<PNT>``
  (first vertex repeated last).  ISO does not require explicit closure but
  it is unambiguous and accepted by the tools checked.
* Files: written as ``<out_dir>/TASKDATA/TASKDATA.XML`` plus
  ``GRD00001.BIN`` (upper-case 8.3 names per ISO 11783-10 convention; the
  ``GRD G`` Filename attribute carries no extension).  With ``zip=True`` a
  ``<out_dir>/TASKDATA.zip`` containing the ``TASKDATA/`` folder is also
  produced and returned.
* Degenerate input: no points/cells raises ``ValueError``; a single point is
  exported as a 1x1 grid with a default 2 m cell so the file stays valid.
"""
from __future__ import annotations

import os
import struct
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nav.geo import latlng_to_local, local_to_latlng

# 1 L/ha = 1e6 mm3 / 1e4 m2 = 100 mm3/m2 (numerically same as kg/ha -> mg/m2)
L_PER_HA_TO_MM3_PER_M2 = 100.0

# Cell edge used when the input has no extent along an axis (single point).
DEFAULT_CELL_M = 2.0

APPLICATION_RATE_DDI = "0006"
GRID_FILENAME = "GRD00001"  # GRD "G" attribute: no extension
GRID_BINARY = "GRD00001.BIN"
TASKDATA_XML = "TASKDATA.XML"

_INT32_MAX = 2**31 - 1


# ------------------------------------------------------------------
# Input normalisation
# ------------------------------------------------------------------


class _NormGrid:
    """Canonical grid: degrees, rows south->north, columns west->east."""

    def __init__(
        self,
        rates: list[list[float]],
        min_north: float,
        min_east: float,
        cell_north: float,
        cell_east: float,
    ) -> None:
        self.rates = rates
        self.min_north = min_north  # lat of the grid's south edge (degrees)
        self.min_east = min_east    # lng of the grid's west edge (degrees)
        self.cell_north = cell_north  # cell height (degrees)
        self.cell_east = cell_east    # cell width (degrees)
        self.rows = len(rates)
        self.cols = len(rates[0])


def _cell_deg(lat0: float, lng0: float, dx_m: float, dy_m: float) -> tuple[float, float]:
    """Convert cell edge lengths in metres to (north_deg, east_deg) at datum."""
    north_deg = local_to_latlng(0.0, dy_m, lat0, lng0)[0] - lat0
    east_deg = local_to_latlng(dx_m, 0.0, lat0, lng0)[1] - lng0
    return north_deg, east_deg


def _normalize_grid_dict(grid: dict) -> _NormGrid:
    """Normalise the PrescriptionMap form: local-metre grid + datum.

    Expects keys: rates (ny x nx, row 0 = south), bounds (xmin, ymin, xmax,
    ymax in local metres, cell centres), lat0, lng0 (datum).
    """
    rates = [list(row) for row in grid["rates"]]
    if not rates or not rates[0]:
        raise ValueError("Prescription grid is empty")
    cols = len(rates[0])
    if any(len(row) != cols for row in rates):
        raise ValueError("Prescription grid rows have unequal lengths")

    xmin, ymin, xmax, ymax = grid["bounds"]
    lat0 = float(grid["lat0"])
    lng0 = float(grid["lng0"])
    rows = len(rates)

    # Grid points are cell centres; edges extend half a step beyond them.
    dx = (xmax - xmin) / (cols - 1) if cols > 1 else DEFAULT_CELL_M
    dy = (ymax - ymin) / (rows - 1) if rows > 1 else DEFAULT_CELL_M

    sw_lat, sw_lng = local_to_latlng(xmin - dx / 2.0, ymin - dy / 2.0, lat0, lng0)
    cell_north, cell_east = _cell_deg(lat0, lng0, dx, dy)
    return _NormGrid(rates, sw_lat, sw_lng, cell_north, cell_east)


def _point_rate(pt: dict) -> float:
    """Rate of a zone/point dict: 'rate' wins, else sum of *_rate keys."""
    if "rate" in pt:
        return float(pt["rate"])
    keys = [k for k in ("n_rate", "p_rate", "k_rate", "total_rate") if k in pt]
    if not keys:
        raise ValueError(
            "Zone point needs a 'rate' (or n_rate/p_rate/k_rate) key"
        )
    if "total_rate" in keys:
        return float(pt["total_rate"])
    return sum(float(pt[k]) for k in keys)


def _axis_step(values: list[float]) -> float:
    """Median gap between consecutive sorted axis values (0 if < 2 values)."""
    if len(values) < 2:
        return 0.0
    gaps = sorted(values[i + 1] - values[i] for i in range(len(values) - 1))
    return gaps[len(gaps) // 2]


def _normalize_points(points: list[dict]) -> _NormGrid:
    """Normalise a list of {lat, lng, rate} zone points onto a lattice.

    Unique latitudes become rows (south -> north) and unique longitudes
    columns (west -> east); cells with no point get rate 0.  A single point
    yields a 1x1 grid with a DEFAULT_CELL_M cell.
    """
    if not points:
        raise ValueError("No prescription data points")

    cells = [
        (round(float(p["lat"]), 8), round(float(p["lng"]), 8), _point_rate(p))
        for p in points
    ]
    lats = sorted({c[0] for c in cells})
    lngs = sorted({c[1] for c in cells})
    row_of = {lat: j for j, lat in enumerate(lats)}
    col_of = {lng: i for i, lng in enumerate(lngs)}

    rates = [[0.0] * len(lngs) for _ in range(len(lats))]
    for lat, lng, rate in cells:
        rates[row_of[lat]][col_of[lng]] = rate

    lat0, lng0 = lats[0], lngs[0]
    default_north, default_east = _cell_deg(lat0, lng0, DEFAULT_CELL_M, DEFAULT_CELL_M)
    cell_north = _axis_step(lats) or default_north
    cell_east = _axis_step(lngs) or default_east

    return _NormGrid(
        rates,
        lats[0] - cell_north / 2.0,
        lngs[0] - cell_east / 2.0,
        cell_north,
        cell_east,
    )


def _normalize(grid_or_zones) -> _NormGrid:
    """Accept either PrescriptionMap's grid dict or a list of zone points."""
    if isinstance(grid_or_zones, dict):
        return _normalize_grid_dict(grid_or_zones)
    return _normalize_points(list(grid_or_zones))


# ------------------------------------------------------------------
# TASKDATA.XML construction
# ------------------------------------------------------------------


def _fmt_deg(value: float) -> str:
    """Decimal degrees with 9 decimals (sub-mm, within ISO's 10-digit cap)."""
    return f"{value:.9f}"


def _boundary_ring(grid: _NormGrid) -> list[tuple[float, float]]:
    """Closed (first == last) SW-SE-NE-NW ring of the grid's outer edge."""
    south, west = grid.min_north, grid.min_east
    north = south + grid.rows * grid.cell_north
    east = west + grid.cols * grid.cell_east
    return [(south, west), (south, east), (north, east), (north, west), (south, west)]


def _partfield_area_m2(grid: _NormGrid) -> int:
    """Approximate grid footprint in m^2 (PFD D is an unsigned integer)."""
    south, west = grid.min_north, grid.min_east
    north = south + grid.rows * grid.cell_north
    east = west + grid.cols * grid.cell_east
    ex, ny = latlng_to_local(north, east, south, west)
    return max(0, int(round(abs(ex) * abs(ny))))


def _build_taskdata(
    grid: _NormGrid,
    product_name: str,
    task_name: str,
    field_name: str,
) -> ET.ElementTree:
    root = ET.Element(
        "ISO11783_TaskData",
        {
            "VersionMajor": "4",
            "VersionMinor": "2",
            "ManagementSoftwareManufacturer": "AgriRover",
            "ManagementSoftwareVersion": "1.0",
            "DataTransferOrigin": "1",  # 1 = created by FMIS
        },
    )

    ET.SubElement(root, "PDT", {"A": "PDT1", "B": product_name})

    pfd = ET.SubElement(
        root,
        "PFD",
        {"A": "PFD1", "C": field_name, "D": str(_partfield_area_m2(grid))},
    )
    pln = ET.SubElement(pfd, "PLN", {"A": "1"})  # 1 = partfield boundary
    lsg = ET.SubElement(pln, "LSG", {"A": "1"})  # 1 = polygon exterior
    for lat, lng in _boundary_ring(grid):
        ET.SubElement(
            lsg, "PNT", {"A": "2", "C": _fmt_deg(lat), "D": _fmt_deg(lng)}
        )

    tsk = ET.SubElement(
        root,
        "TSK",
        {"A": "TSK1", "B": task_name, "E": "PFD1", "G": "1"},  # G=1: planned
    )
    tzn = ET.SubElement(tsk, "TZN", {"A": "1", "B": "Application rate"})
    ET.SubElement(
        tzn,
        "PDV",
        {"A": APPLICATION_RATE_DDI, "B": "0", "C": "PDT1"},
    )
    ET.SubElement(
        tsk,
        "GRD",
        {
            "A": _fmt_deg(grid.min_north),
            "B": _fmt_deg(grid.min_east),
            "C": _fmt_deg(grid.cell_north),
            "D": _fmt_deg(grid.cell_east),
            "E": str(grid.cols),
            "F": str(grid.rows),
            "G": GRID_FILENAME,
            "H": str(grid.rows * grid.cols * 4),
            "I": "2",  # GridType 2: cell values live in the binary
            "J": "1",  # TreatmentZoneCode -> TZN A="1"
        },
    )

    tree = ET.ElementTree(root)
    ET.indent(tree)
    return tree


def _grid_binary(grid: _NormGrid, factor: float) -> bytes:
    """Little-endian int32 cells, row-major from the south-west corner."""
    values = []
    for row in grid.rates:  # row 0 = southernmost, rows south -> north
        for rate in row:    # columns west -> east
            scaled = int(round(rate * factor))
            values.append(min(max(scaled, 0), _INT32_MAX))
    return struct.pack(f"<{len(values)}i", *values)


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------


def export_isoxml(
    grid_or_zones,
    out_dir: str | Path,
    product_name: str = "NPK blend",
    rate_unit_l_per_ha: bool = True,
    task_name: str = "AgriRover prescription",
    field_name: str = "AgriRover field",
    zip: bool = False,
) -> Path:
    """Export a prescription map as an ISO 11783-10 TASKDATA file set.

    grid_or_zones is either the dict PrescriptionMap produces
    ({"rates": ny x nx list, "bounds": local-metre (xmin, ymin, xmax, ymax)
    of cell centres, "lat0": ..., "lng0": ...}) or a list of zone points
    ({"lat", "lng", "rate"} dicts, lattice inferred).  Rates are L/ha by
    default and converted at 1 L/ha = 100 mm3/m2; pass
    ``rate_unit_l_per_ha=False`` for values already in mm3/m2.

    Writes <out_dir>/TASKDATA/TASKDATA.XML and GRD00001.BIN and returns the
    TASKDATA directory; with ``zip=True`` also writes <out_dir>/TASKDATA.zip
    and returns the zip path instead.
    """
    grid = _normalize(grid_or_zones)
    factor = L_PER_HA_TO_MM3_PER_M2 if rate_unit_l_per_ha else 1.0

    out_dir = Path(out_dir)
    taskdata_dir = out_dir / "TASKDATA"
    taskdata_dir.mkdir(parents=True, exist_ok=True)

    tree = _build_taskdata(grid, product_name, task_name, field_name)
    tree.write(taskdata_dir / TASKDATA_XML, encoding="utf-8", xml_declaration=True)
    (taskdata_dir / GRID_BINARY).write_bytes(_grid_binary(grid, factor))

    if zip:
        zip_path = out_dir / "TASKDATA.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in (TASKDATA_XML, GRID_BINARY):
                zf.write(taskdata_dir / name, f"TASKDATA/{name}")
        return zip_path

    return taskdata_dir
