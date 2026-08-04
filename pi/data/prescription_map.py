"""Variable-rate application (prescription) map exporter.

Reads soil NPK data from field log CSVs or direct point lists, interpolates
via IDW onto a regular grid, computes per-cell application rates based on
configurable target nutrient levels, and exports the result as CSV and GeoJSON
for use in precision-ag tools or the dashboard.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nav.geo import latlng_to_local, local_to_latlng

from data.heatmap import idw_grid
from data.isoxml import export_isoxml


class PrescriptionMap:
    """Compute and export variable-rate prescription maps from soil readings."""

    def __init__(
        self,
        target_n: float = 40.0,
        target_p: float = 20.0,
        target_k: float = 30.0,
        grid_size: int = 20,
    ) -> None:
        self.target_n = target_n
        self.target_p = target_p
        self.target_k = target_k
        self.grid_size = grid_size
        self._points: list[dict[str, float]] = []

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def load_csv(self, path: str) -> None:
        """Load points from a field_log CSV (pathway_stream format).

        Filters to rows where gps_fix == 1 and extracts lat, lng, n, p, k.
        """
        with open(path, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row.get("gps_fix", "0") != "1":
                    continue
                try:
                    self._points.append({
                        "lat": float(row["lat"]),
                        "lng": float(row["lng"]),
                        "n": float(row["n"]),
                        "p": float(row["p"]),
                        "k": float(row["k"]),
                    })
                except (KeyError, ValueError):
                    continue

    def load_points(self, points: list[dict[str, float]]) -> None:
        """Accept a list of dicts with keys: lat, lng, n, p, k."""
        for pt in points:
            self._points.append({
                "lat": float(pt["lat"]),
                "lng": float(pt["lng"]),
                "n": float(pt["n"]),
                "p": float(pt["p"]),
                "k": float(pt["k"]),
            })

    # ------------------------------------------------------------------
    # Grid computation
    # ------------------------------------------------------------------

    def _compute_grid(self) -> tuple[
        list[list[float]],
        list[list[float]],
        list[list[float]],
        tuple[float, float, float, float],
        float,
        float,
    ]:
        """Interpolate nutrients and compute application rates on a grid.

        Returns (n_rate_grid, p_rate_grid, k_rate_grid, bounds, lat0, lng0).
        Each grid is ny x nx with rate = max(0, target - interpolated).
        """
        if not self._points:
            raise ValueError("No data points loaded")

        # Use first point as datum for local coordinate conversion
        lat0 = self._points[0]["lat"]
        lng0 = self._points[0]["lng"]

        # Convert to local metres and build per-nutrient point lists
        n_pts: list[tuple[float, float, float]] = []
        p_pts: list[tuple[float, float, float]] = []
        k_pts: list[tuple[float, float, float]] = []

        for pt in self._points:
            east, north = latlng_to_local(pt["lat"], pt["lng"], lat0, lng0)
            n_pts.append((east, north, pt["n"]))
            p_pts.append((east, north, pt["p"]))
            k_pts.append((east, north, pt["k"]))

        # Determine bounds in local coords
        all_east = [p[0] for p in n_pts]
        all_north = [p[1] for p in n_pts]
        xmin, xmax = min(all_east), max(all_east)
        ymin, ymax = min(all_north), max(all_north)

        # Ensure non-zero extent
        if xmax - xmin < 1e-6:
            xmin -= 1.0
            xmax += 1.0
        if ymax - ymin < 1e-6:
            ymin -= 1.0
            ymax += 1.0

        bounds = (xmin, ymin, xmax, ymax)
        nx = ny = self.grid_size

        # Interpolate each nutrient
        n_grid = idw_grid(n_pts, bounds, nx, ny)
        p_grid = idw_grid(p_pts, bounds, nx, ny)
        k_grid = idw_grid(k_pts, bounds, nx, ny)

        # Compute application rates: rate = max(0, target - interpolated)
        n_rate = [
            [max(0.0, self.target_n - n_grid[j][i]) for i in range(nx)]
            for j in range(ny)
        ]
        p_rate = [
            [max(0.0, self.target_p - p_grid[j][i]) for i in range(nx)]
            for j in range(ny)
        ]
        k_rate = [
            [max(0.0, self.target_k - k_grid[j][i]) for i in range(nx)]
            for j in range(ny)
        ]

        return n_rate, p_rate, k_rate, bounds, lat0, lng0

    # ------------------------------------------------------------------
    # Export methods
    # ------------------------------------------------------------------

    def export_csv(self, path: str) -> None:
        """Write prescription map as CSV with columns:

        lat, lng, n_rate_kg_ha, p_rate_kg_ha, k_rate_kg_ha
        """
        n_rate, p_rate, k_rate, bounds, lat0, lng0 = self._compute_grid()
        xmin, ymin, xmax, ymax = bounds
        nx = ny = self.grid_size

        with open(path, "w", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["lat", "lng", "n_rate_kg_ha", "p_rate_kg_ha", "k_rate_kg_ha"])
            for j in range(ny):
                gy = ymin + (ymax - ymin) * (j / max(1, ny - 1))
                for i in range(nx):
                    gx = xmin + (xmax - xmin) * (i / max(1, nx - 1))
                    lat, lng = local_to_latlng(gx, gy, lat0, lng0)
                    writer.writerow([
                        f"{lat:.8f}",
                        f"{lng:.8f}",
                        f"{n_rate[j][i]:.2f}",
                        f"{p_rate[j][i]:.2f}",
                        f"{k_rate[j][i]:.2f}",
                    ])

    def export_geojson(self, path: str) -> None:
        """Write prescription map as GeoJSON FeatureCollection.

        Each grid cell is a Polygon feature with properties:
        n_rate, p_rate, k_rate, total_rate.
        """
        n_rate, p_rate, k_rate, bounds, lat0, lng0 = self._compute_grid()
        xmin, ymin, xmax, ymax = bounds
        nx = ny = self.grid_size

        dx = (xmax - xmin) / max(1, nx - 1)
        dy = (ymax - ymin) / max(1, ny - 1)

        features: list[dict] = []
        for j in range(ny):
            gy = ymin + (ymax - ymin) * (j / max(1, ny - 1))
            for i in range(nx):
                gx = xmin + (xmax - xmin) * (i / max(1, nx - 1))

                # Cell corners (half-step in each direction)
                hdx = dx / 2.0
                hdy = dy / 2.0
                corners_local = [
                    (gx - hdx, gy - hdy),
                    (gx + hdx, gy - hdy),
                    (gx + hdx, gy + hdy),
                    (gx - hdx, gy + hdy),
                    (gx - hdx, gy - hdy),  # close ring
                ]
                # Convert to lat/lng (GeoJSON uses [lng, lat] order)
                ring = []
                for ex, ny_ in corners_local:
                    lat, lng = local_to_latlng(ex, ny_, lat0, lng0)
                    ring.append([lng, lat])

                nr = n_rate[j][i]
                pr = p_rate[j][i]
                kr = k_rate[j][i]

                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [ring],
                    },
                    "properties": {
                        "n_rate": round(nr, 2),
                        "p_rate": round(pr, 2),
                        "k_rate": round(kr, 2),
                        "total_rate": round(nr + pr + kr, 2),
                    },
                }
                features.append(feature)

        collection = {
            "type": "FeatureCollection",
            "features": features,
        }

        with open(path, "w") as fh:
            json.dump(collection, fh, indent=2)

    def to_isoxml(
        self,
        out_dir: str,
        nutrient: str = "total",
        product_name: str = "NPK blend",
        zip: bool = False,
    ):
        """Export as an ISO 11783-10 (ISOXML) TASKDATA set via data.isoxml.

        nutrient selects the rate grid: "n", "p", "k" or "total" (sum).
        Rates are kg/ha, encoded x100 per the isoxml module's conventions
        (same factor as its L/ha default).  Returns the TASKDATA directory
        path, or the .zip path when zip=True.
        """
        n_rate, p_rate, k_rate, bounds, lat0, lng0 = self._compute_grid()
        grids = {"n": n_rate, "p": p_rate, "k": k_rate}
        if nutrient == "total":
            rates = [
                [n_rate[j][i] + p_rate[j][i] + k_rate[j][i] for i in range(len(n_rate[0]))]
                for j in range(len(n_rate))
            ]
        elif nutrient in grids:
            rates = grids[nutrient]
        else:
            raise ValueError(f"Unknown nutrient {nutrient!r} (use n, p, k or total)")

        return export_isoxml(
            {"rates": rates, "bounds": bounds, "lat0": lat0, "lng0": lng0},
            out_dir,
            product_name=product_name,
            zip=zip,
        )


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------


def main() -> None:
    """CLI for generating prescription maps from field log CSVs."""
    parser = argparse.ArgumentParser(
        description="Generate variable-rate prescription maps from soil data."
    )
    parser.add_argument("--input", required=True, help="Path to field_log CSV")
    parser.add_argument("--output-csv", help="Output CSV path")
    parser.add_argument("--output-geojson", help="Output GeoJSON path")
    parser.add_argument("--grid-size", type=int, default=20, help="Grid resolution (default: 20)")
    parser.add_argument("--target-n", type=float, default=40.0, help="Target N (mg/kg, default: 40)")
    parser.add_argument("--target-p", type=float, default=20.0, help="Target P (mg/kg, default: 20)")
    parser.add_argument("--target-k", type=float, default=30.0, help="Target K (mg/kg, default: 30)")

    args = parser.parse_args()

    pm = PrescriptionMap(
        target_n=args.target_n,
        target_p=args.target_p,
        target_k=args.target_k,
        grid_size=args.grid_size,
    )
    pm.load_csv(args.input)

    if args.output_csv:
        pm.export_csv(args.output_csv)
        print(f"CSV written to {args.output_csv}")

    if args.output_geojson:
        pm.export_geojson(args.output_geojson)
        print(f"GeoJSON written to {args.output_geojson}")

    if not args.output_csv and not args.output_geojson:
        print("No output specified. Use --output-csv and/or --output-geojson.")


if __name__ == "__main__":
    main()
