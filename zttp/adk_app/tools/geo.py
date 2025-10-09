"""Geospatial helpers for lightweight routing logic."""

from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from typing import Dict, Iterable, List, Sequence


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return r * c


def distance_matrix_local(points: Sequence[Dict[str, float]]) -> List[List[float]]:
    matrix: List[List[float]] = []
    for i, src in enumerate(points):
        row = []
        for j, dst in enumerate(points):
            if i == j:
                row.append(0.0)
            else:
                row.append(
                    haversine_distance_km(
                        src.get("lat", 0.0),
                        src.get("lon", 0.0),
                        dst.get("lat", 0.0),
                        dst.get("lon", 0.0),
                    )
                )
        matrix.append(row)
    return matrix


def cluster_points(points: Iterable[Dict[str, float]], buckets: int) -> List[List[Dict[str, float]]]:
    point_list = list(points)
    if buckets <= 0:
        return [point_list]
    bucket_size = max(1, len(point_list) // buckets)
    clusters: List[List[Dict[str, float]]] = []
    for start in range(0, len(point_list), bucket_size):
        clusters.append(point_list[start : start + bucket_size])
    while len(clusters) < buckets:
        clusters.append([])
    return clusters[:buckets]

