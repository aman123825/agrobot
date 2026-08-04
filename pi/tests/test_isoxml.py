"""Tests for the ISO 11783-10 (ISOXML) prescription-map exporter."""
import struct
import xml.etree.ElementTree as ET
import zipfile

import pytest

from data.isoxml import L_PER_HA_TO_MM3_PER_M2, export_isoxml
from data.prescription_map import PrescriptionMap

LAT0, LNG0 = 19.0, 72.9


def grid_payload(rates, bounds=(0.0, 0.0, 20.0, 10.0), lat0=LAT0, lng0=LNG0):
    """Build the dict form PrescriptionMap passes to export_isoxml."""
    return {"rates": rates, "bounds": bounds, "lat0": lat0, "lng0": lng0}


def export_and_parse(tmp_path, rates=None, **kwargs):
    """Export a small grid and return (taskdata_dir, parsed XML root)."""
    if rates is None:
        rates = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    out = export_isoxml(grid_payload(rates), tmp_path, **kwargs)
    root = ET.parse(out / "TASKDATA.XML").getroot()
    return out, root


class TestTaskDataXml:
    def test_root_and_required_elements(self, tmp_path):
        _, root = export_and_parse(tmp_path)
        assert root.tag == "ISO11783_TaskData"
        assert root.get("VersionMajor") == "4"
        assert root.get("VersionMinor") == "2"
        assert root.get("ManagementSoftwareManufacturer") == "AgriRover"
        assert root.get("DataTransferOrigin") == "1"
        for tag in ("PDT", "PFD", "TSK"):
            assert root.find(tag) is not None

    def test_grd_attributes(self, tmp_path):
        _, root = export_and_parse(tmp_path)
        grd = root.find("TSK/GRD")
        assert grd is not None
        assert grd.get("I") == "2"                    # GridType 2
        assert grd.get("G") == "GRD00001"             # Filename, no extension
        assert grd.get("E") == "3" and grd.get("F") == "2"  # cols x rows
        assert grd.get("H") == str(2 * 3 * 4)         # FileLength
        # Minimum position is south-west of the datum (cell centres at 0,0)
        assert float(grd.get("A")) < LAT0
        assert float(grd.get("B")) < LNG0
        assert float(grd.get("C")) > 0 and float(grd.get("D")) > 0

    def test_task_links_partfield_product_and_zone(self, tmp_path):
        _, root = export_and_parse(tmp_path, product_name="urea mix")
        tsk = root.find("TSK")
        assert tsk.get("G") == "1"                    # TaskStatus: planned
        assert tsk.get("E") == root.find("PFD").get("A")
        tzn = tsk.find("TZN")
        assert tzn.get("A") == tsk.find("GRD").get("J")
        pdv = tzn.find("PDV")
        assert pdv.get("A") == "0006"                 # application-rate DDI
        assert pdv.get("C") == root.find("PDT").get("A")
        assert root.find("PDT").get("B") == "urea mix"


class TestGridBinary:
    def test_size_and_roundtrip_sw_row_major(self, tmp_path):
        out, root = export_and_parse(tmp_path)
        blob = (out / "GRD00001.BIN").read_bytes()
        grd = root.find("TSK/GRD")
        rows, cols = int(grd.get("F")), int(grd.get("E"))
        assert len(blob) == rows * cols * 4
        values = struct.unpack(f"<{rows * cols}i", blob)
        # Row 0 (south) west->east first, then the northern row
        assert values == (100, 200, 300, 400, 500, 600)

    def test_l_per_ha_to_mm3_per_m2(self, tmp_path):
        assert L_PER_HA_TO_MM3_PER_M2 == 100.0
        out = export_isoxml(grid_payload([[2.5]]), tmp_path)
        assert struct.unpack("<i", (out / "GRD00001.BIN").read_bytes()) == (250,)

    def test_raw_unit_passthrough(self, tmp_path):
        out = export_isoxml(
            grid_payload([[7.0]]), tmp_path, rate_unit_l_per_ha=False
        )
        assert struct.unpack("<i", (out / "GRD00001.BIN").read_bytes()) == (7,)

    def test_negatives_clamped_and_values_rounded(self, tmp_path):
        out = export_isoxml(grid_payload([[-5.0, 0.014]]), tmp_path)
        values = struct.unpack("<2i", (out / "GRD00001.BIN").read_bytes())
        assert values == (0, 1)  # clamp to 0; 1.4 mm3/m2 rounds to 1


class TestBoundaryPolygon:
    def test_closed_ring_matches_grid_extent(self, tmp_path):
        _, root = export_and_parse(tmp_path)
        pln = root.find("PFD/PLN")
        assert pln.get("A") == "1"                    # partfield boundary
        lsg = pln.find("LSG")
        assert lsg.get("A") == "1"                    # polygon exterior
        pnts = lsg.findall("PNT")
        assert len(pnts) >= 3
        first, last = pnts[0], pnts[-1]
        assert (first.get("C"), first.get("D")) == (last.get("C"), last.get("D"))
        # South-west vertex coincides with the grid minimum position
        grd = root.find("TSK/GRD")
        assert first.get("C") == grd.get("A") and first.get("D") == grd.get("B")
        assert all(p.get("A") == "2" for p in pnts)


class TestZipOption:
    def test_zip_contains_taskdata(self, tmp_path):
        path = export_isoxml(grid_payload([[1.0]]), tmp_path, zip=True)
        assert path.name == "TASKDATA.zip"
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
        assert "TASKDATA/TASKDATA.XML" in names
        assert "TASKDATA/GRD00001.BIN" in names


class TestDegenerateInput:
    def test_empty_points_raise(self, tmp_path):
        with pytest.raises(ValueError):
            export_isoxml([], tmp_path)

    def test_empty_grid_raises(self, tmp_path):
        with pytest.raises(ValueError):
            export_isoxml(grid_payload([]), tmp_path)

    def test_single_point_yields_one_cell_grid(self, tmp_path):
        out = export_isoxml([{"lat": LAT0, "lng": LNG0, "rate": 4.0}], tmp_path)
        root = ET.parse(out / "TASKDATA.XML").getroot()
        grd = root.find("TSK/GRD")
        assert grd.get("E") == "1" and grd.get("F") == "1"
        assert struct.unpack("<i", (out / "GRD00001.BIN").read_bytes()) == (400,)


class TestPointListForm:
    def test_lattice_placement_and_missing_cell_zero(self, tmp_path):
        # 2x2 lattice with the north-east cell missing -> that cell is 0
        points = [
            {"lat": LAT0, "lng": LNG0, "rate": 1.0},              # SW
            {"lat": LAT0, "lng": LNG0 + 1e-4, "rate": 2.0},       # SE
            {"lat": LAT0 + 1e-4, "lng": LNG0, "rate": 3.0},       # NW
        ]
        out = export_isoxml(points, tmp_path)
        values = struct.unpack("<4i", (out / "GRD00001.BIN").read_bytes())
        assert values == (100, 200, 300, 0)


class TestPrescriptionMapWrapper:
    POINTS = [
        {"lat": LAT0, "lng": LNG0, "n": 10, "p": 5, "k": 8},
        {"lat": LAT0 + 2e-4, "lng": LNG0 + 1e-4, "n": 35, "p": 18, "k": 25},
        {"lat": LAT0 + 1e-4, "lng": LNG0 + 2e-4, "n": 20, "p": 10, "k": 15},
    ]

    def test_to_isoxml_writes_taskdata(self, tmp_path):
        pm = PrescriptionMap(grid_size=4)
        pm.load_points(self.POINTS)
        out = pm.to_isoxml(str(tmp_path))
        assert (out / "TASKDATA.XML").is_file()
        blob = (out / "GRD00001.BIN").read_bytes()
        assert len(blob) == 4 * 4 * 4
        root = ET.parse(out / "TASKDATA.XML").getroot()
        assert root.find("TSK/GRD").get("I") == "2"
        # Deficits exist (readings below target), so some rate must be > 0
        assert max(struct.unpack("<16i", blob)) > 0

    def test_unknown_nutrient_raises(self, tmp_path):
        pm = PrescriptionMap(grid_size=4)
        pm.load_points(self.POINTS)
        with pytest.raises(ValueError):
            pm.to_isoxml(str(tmp_path), nutrient="zn")
