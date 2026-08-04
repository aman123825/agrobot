"""Zone helpers: bounding-box computation and coverage waypoint generation.

Integrates with nav/geo and nav/path_planner to convert a zone boundary
(list of lat/lng waypoints) into an ordered list of coverage waypoints using
boustrophedon planning.

This is a utility module used when creating missions with zone coverage.
The MissionScheduler stores zone definitions and callers invoke
zone_waypoints() to expand a zone boundary into a full coverage path before
sending waypoints to the rover.  It is not imported by the scheduler itself
because waypoint expansion is the responsibility of the orchestrator or
mission creator at mission-add time.
"""
from __future__ import annotations

import os
import sys

# Allow relative imports when running from the pi/ directory.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nav.geo import latlng_to_local, local_to_latlng
from nav.path_planner import boustrophedon


def zone_bounds(
    waypoints: list[tuple[float, float]],
) -> tuple[float, float, float, float]:
    """Compute the geographic bounding box of a list of (lat, lng) waypoints.

    Returns (min_lat, min_lng, max_lat, max_lng).
    """
    if not waypoints:
        raise ValueError("waypoints must not be empty")
    lats = [w[0] for w in waypoints]
    lngs = [w[1] for w in waypoints]
    return (min(lats), min(lngs), max(lats), max(lngs))


def zone_waypoints(
    waypoints: list[tuple[float, float]],
    row_spacing_m: float = 1.0,
) -> list[tuple[float, float]]:
    """Generate coverage waypoints for a zone defined by boundary points.

    Steps:
      1. Convert boundary waypoints to local meters (first point as datum).
      2. Compute the local bounding box (width x length).
      3. Generate boustrophedon coverage path via path_planner.
      4. Convert resulting waypoints back to lat/lng.

    Returns an ordered list of (lat, lng) waypoints for the coverage path.
    """
    if not waypoints or len(waypoints) < 2:
        raise ValueError("Need at least 2 boundary waypoints")

    # Use first waypoint as the datum for local conversion
    lat0, lng0 = waypoints[0]

    # Convert all boundary points to local meters
    local_pts = [latlng_to_local(lat, lng, lat0, lng0) for lat, lng in waypoints]

    # Compute bounding box in local coordinates
    easts = [p[0] for p in local_pts]
    norths = [p[1] for p in local_pts]
    min_e, max_e = min(easts), max(easts)
    min_n, max_n = min(norths), max(norths)

    width = max_e - min_e
    length = max_n - min_n

    # Generate boustrophedon coverage pattern
    origin = (min_e, min_n)
    local_coverage = boustrophedon(width, length, row_spacing_m, origin)

    # Convert back to lat/lng
    return [local_to_latlng(e, n, lat0, lng0) for e, n in local_coverage]
