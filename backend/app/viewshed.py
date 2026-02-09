from __future__ import annotations

import math

import numpy as np

EARTH_RADIUS_M = 6_371_000.0


def compute_viewshed(
  dem: np.ndarray,
  observer_rc: tuple[int, int],
  observer_height_m: float,
  cell_size_m: float,
  curvature_enabled: bool = False,
) -> np.ndarray:
  """
  Compute a boolean visibility mask for a DEM using a radial sweep / horizon method.

  dem: 2D array of elevations (meters)
  observer_rc: (row, col) index of the observer in the DEM
  observer_height_m: observer height above ground (meters)
  cell_size_m: square cell size (meters)
  """

  return _compute_viewshed_baseline(dem, observer_rc, observer_height_m, cell_size_m, curvature_enabled)


def compute_viewshed_radial(
  dem: np.ndarray,
  observer_rc: tuple[int, int],
  observer_height_m: float,
  cell_size_m: float,
  curvature_enabled: bool = False,
) -> np.ndarray:
  """
  Compute a visibility mask using a radial sweep / horizon method (faster, less accurate).
  """

  return _compute_viewshed_radial(dem, observer_rc, observer_height_m, cell_size_m, curvature_enabled)


def smooth_visibility_mask(mask: np.ndarray, passes: int = 1, threshold: int | None = None) -> np.ndarray:
  """
  Reduce speckle by applying a majority filter over a 3x3 neighborhood.
  """

  if mask.ndim != 2:
    raise ValueError("mask must be a 2D array.")
  if passes < 1:
    return mask

  current = mask.astype(np.uint8)
  for _ in range(passes):
    padded = np.pad(current, 1, mode="constant", constant_values=0)
    window_sum = (
      padded[0:-2, 0:-2]
      + padded[0:-2, 1:-1]
      + padded[0:-2, 2:]
      + padded[1:-1, 0:-2]
      + padded[1:-1, 1:-1]
      + padded[1:-1, 2:]
      + padded[2:, 0:-2]
      + padded[2:, 1:-1]
      + padded[2:, 2:]
    )
    required = threshold if threshold is not None else 5
    current = (window_sum >= required).astype(np.uint8)

  return current.astype(bool)


def compute_viewshed_baseline(
  dem: np.ndarray,
  observer_rc: tuple[int, int],
  observer_height_m: float,
  cell_size_m: float,
  curvature_enabled: bool = False,
) -> np.ndarray:
  """
  Baseline (slow) line-of-sight sampling implementation.
  Kept for correctness checks and benchmarking.
  """

  return _compute_viewshed_baseline(dem, observer_rc, observer_height_m, cell_size_m, curvature_enabled)


def _compute_viewshed_radial(
  dem: np.ndarray,
  observer_rc: tuple[int, int],
  observer_height_m: float,
  cell_size_m: float,
  curvature_enabled: bool = False,
) -> np.ndarray:
  _validate_inputs(dem, observer_rc, observer_height_m, cell_size_m)

  rows, cols = dem.shape
  obs_r, obs_c = observer_rc
  observer_ground = float(dem[obs_r, obs_c])
  if math.isnan(observer_ground):
    raise ValueError("Observer elevation is NaN.")

  observer_elevation = observer_ground + observer_height_m
  visibility = np.zeros((rows, cols), dtype=bool)
  visibility[obs_r, obs_c] = True

  rays: dict[tuple[int, int], list[tuple[int, int, int, float]]] = {}

  for r in range(rows):
    for c in range(cols):
      if r == obs_r and c == obs_c:
        continue
      target = float(dem[r, c])
      if math.isnan(target):
        continue

      dr = r - obs_r
      dc = c - obs_c
      g = math.gcd(abs(dr), abs(dc))
      if g == 0:
        continue
      direction = (dr // g, dc // g)

      distance = math.hypot(dr, dc) * cell_size_m
      target_effective = target
      if curvature_enabled and distance > 0:
        target_effective = target - _curvature_drop(distance)
      angle = math.atan2(target_effective - observer_elevation, distance)

      rays.setdefault(direction, []).append((g, r, c, angle))

  epsilon = 1e-12
  for entries in rays.values():
    entries.sort(key=lambda item: item[0])
    max_angle = -math.inf
    for _, r, c, angle in entries:
      if angle >= max_angle - epsilon:
        visibility[r, c] = True
        if angle > max_angle:
          max_angle = angle

  return visibility


def _compute_viewshed_baseline(
  dem: np.ndarray,
  observer_rc: tuple[int, int],
  observer_height_m: float,
  cell_size_m: float,
  curvature_enabled: bool = False,
) -> np.ndarray:
  _validate_inputs(dem, observer_rc, observer_height_m, cell_size_m)

  rows, cols = dem.shape
  obs_r, obs_c = observer_rc
  observer_ground = float(dem[obs_r, obs_c])
  if math.isnan(observer_ground):
    raise ValueError("Observer elevation is NaN.")

  observer_elevation = observer_ground + observer_height_m

  visibility = np.zeros((rows, cols), dtype=bool)
  visibility[obs_r, obs_c] = True

  for r in range(rows):
    for c in range(cols):
      if r == obs_r and c == obs_c:
        continue
      target = float(dem[r, c])
      if math.isnan(target):
        continue
      if _line_of_sight(
        dem,
        observer_elevation,
        target,
        (obs_r, obs_c),
        (r, c),
        cell_size_m,
        curvature_enabled,
      ):
        visibility[r, c] = True

  return visibility


def _validate_inputs(
  dem: np.ndarray,
  observer_rc: tuple[int, int],
  observer_height_m: float,
  cell_size_m: float,
) -> None:
  if dem.ndim != 2:
    raise ValueError("DEM must be a 2D array.")
  if cell_size_m <= 0:
    raise ValueError("cell_size_m must be positive.")
  if observer_height_m < 0:
    raise ValueError("observer_height_m must be non-negative.")

  rows, cols = dem.shape
  obs_r, obs_c = observer_rc
  if not (0 <= obs_r < rows and 0 <= obs_c < cols):
    raise IndexError("Observer index out of bounds.")


def _line_of_sight(
  dem: np.ndarray,
  observer_elevation: float,
  target_elevation: float,
  observer_rc: tuple[int, int],
  target_rc: tuple[int, int],
  cell_size_m: float,
  curvature_enabled: bool = False,
) -> bool:
  obs_r, obs_c = observer_rc
  tgt_r, tgt_c = target_rc

  dr = tgt_r - obs_r
  dc = tgt_c - obs_c
  steps = int(max(abs(dr), abs(dc)))
  if steps == 0:
    return True

  total_distance = math.hypot(dr, dc) * cell_size_m
  target_effective = target_elevation
  if curvature_enabled and total_distance > 0:
    target_effective = target_elevation - _curvature_drop(total_distance)

  # Sample along the line at grid-cell intervals.
  for step in range(1, steps):
    t = step / steps
    r = obs_r + dr * t
    c = obs_c + dc * t

    terrain = _bilinear_sample(dem, r, c)
    if math.isnan(terrain):
      return False

    distance = total_distance * t
    expected = observer_elevation + (target_effective - observer_elevation) * t
    if curvature_enabled and distance > 0:
      terrain = terrain - _curvature_drop(distance)
    if terrain > expected:
      return False

  return True


def _curvature_drop(distance_m: float) -> float:
  return (distance_m * distance_m) / (2.0 * EARTH_RADIUS_M)


def _bilinear_sample(dem: np.ndarray, row: float, col: float) -> float:
  rows, cols = dem.shape

  r0 = int(math.floor(row))
  c0 = int(math.floor(col))
  r1 = min(r0 + 1, rows - 1)
  c1 = min(c0 + 1, cols - 1)

  if r0 < 0 or c0 < 0 or r0 >= rows or c0 >= cols:
    return float("nan")

  dr = row - r0
  dc = col - c0

  e00 = float(dem[r0, c0])
  e10 = float(dem[r1, c0])
  e01 = float(dem[r0, c1])
  e11 = float(dem[r1, c1])

  if any(math.isnan(value) for value in (e00, e10, e01, e11)):
    return float("nan")

  return (
    e00 * (1 - dr) * (1 - dc)
    + e10 * dr * (1 - dc)
    + e01 * (1 - dr) * dc
    + e11 * dr * dc
  )
