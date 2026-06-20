"""Geodetic <-> local-tangent-plane conversion (equirectangular).

Accurate to well under a meter over a single field, which is all we need to
fuse GPS with odometry in a common metric frame.
"""
from __future__ import annotations

import math

_EARTH_R = 6378137.0  # WGS84 mean radius (m)


def latlng_to_local(lat: float, lng: float, lat0: float, lng0: float) -> tuple[float, float]:
    """Return (east_m, north_m) of (lat,lng) relative to datum (lat0,lng0)."""
    east = math.radians(lng - lng0) * _EARTH_R * math.cos(math.radians(lat0))
    north = math.radians(lat - lat0) * _EARTH_R
    return (east, north)


def local_to_latlng(east: float, north: float, lat0: float, lng0: float) -> tuple[float, float]:
    """Inverse of latlng_to_local."""
    lat = lat0 + math.degrees(north / _EARTH_R)
    lng = lng0 + math.degrees(east / (_EARTH_R * math.cos(math.radians(lat0))))
    return (lat, lng)
