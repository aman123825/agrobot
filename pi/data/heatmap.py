"""Spatial interpolation of point soil readings into a field grid.

IDW (inverse-distance weighting) is implemented in pure Python (no deps) so it
always works; if pykrige is installed, `krige_grid` offers ordinary kriging for
smoother maps. The grid feeds the dashboard heatmap and variable-rate maps.
"""
from __future__ import annotations

import logging
import math

logger = logging.getLogger(__name__)


def idw_interpolate(points: list[tuple[float, float, float]], qx: float, qy: float,
                    power: float = 2.0) -> float:
    """Inverse-distance-weighted value at (qx,qy) from (x,y,value) points."""
    if not points:
        return 0.0
    num = 0.0
    den = 0.0
    for x, y, val in points:
        d2 = (x - qx) ** 2 + (y - qy) ** 2
        if d2 < 1e-12:
            return val  # exact hit
        w = 1.0 / (math.sqrt(d2) ** power)
        num += w * val
        den += w
    return num / den if den else 0.0


def idw_grid(points: list[tuple[float, float, float]],
             bounds: tuple[float, float, float, float],
             nx: int = 40, ny: int = 40, power: float = 2.0) -> list[list[float]]:
    """Return an ny x nx grid of IDW values over bounds=(xmin,ymin,xmax,ymax)."""
    xmin, ymin, xmax, ymax = bounds
    grid = [[0.0] * nx for _ in range(ny)]
    for j in range(ny):
        gy = ymin + (ymax - ymin) * (j / max(1, ny - 1))
        for i in range(nx):
            gx = xmin + (xmax - xmin) * (i / max(1, nx - 1))
            grid[j][i] = idw_interpolate(points, gx, gy, power)
    return grid


def krige_grid(points: list[tuple[float, float, float]],
               bounds: tuple[float, float, float, float],
               nx: int = 40, ny: int = 40):
    """Ordinary kriging via pykrige if available; falls back to IDW otherwise."""
    try:
        import numpy as np
        from pykrige.ok import OrdinaryKriging

        xs = np.array([p[0] for p in points])
        ys = np.array([p[1] for p in points])
        vs = np.array([p[2] for p in points])
        xmin, ymin, xmax, ymax = bounds
        gx = np.linspace(xmin, xmax, nx)
        gy = np.linspace(ymin, ymax, ny)
        ok = OrdinaryKriging(xs, ys, vs, variogram_model="spherical")
        z, _ = ok.execute("grid", gx, gy)
        return z
    except Exception as exc:
        logger.info("kriging unavailable (%s); using IDW", exc)
        return idw_grid(points, bounds, nx, ny)
