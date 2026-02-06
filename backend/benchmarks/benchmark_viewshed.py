import time

import numpy as np

from app.viewshed import compute_viewshed, compute_viewshed_baseline


def _make_dem(size: int, seed: int = 42) -> np.ndarray:
  rng = np.random.default_rng(seed)
  base = rng.normal(loc=200.0, scale=50.0, size=(size, size)).astype(np.float64)
  # Smooth slightly to avoid extreme spikes.
  kernel = np.array([[1, 2, 1], [2, 4, 2], [1, 2, 1]], dtype=np.float64)
  kernel /= kernel.sum()
  padded = np.pad(base, 1, mode="edge")
  smoothed = np.zeros_like(base)
  for r in range(size):
    for c in range(size):
      window = padded[r : r + 3, c : c + 3]
      smoothed[r, c] = float((window * kernel).sum())
  return smoothed


def _time(label: str, fn, repeats: int = 1) -> float:
  durations = []
  for _ in range(repeats):
    start = time.perf_counter()
    fn()
    durations.append(time.perf_counter() - start)
  avg = sum(durations) / len(durations)
  print(f"{label}: {avg:.3f}s (avg of {repeats})")
  return avg


def main() -> None:
  size = 200
  dem = _make_dem(size)
  observer = (size // 2, size // 2)

  print("Benchmarking viewshed implementations")
  print(f"Grid: {size}x{size}")

  # Warm-up
  compute_viewshed(dem, observer, observer_height_m=1.7, cell_size_m=30.0)
  compute_viewshed_baseline(dem, observer, observer_height_m=1.7, cell_size_m=30.0)

  _time(
    "Radial sweep",
    lambda: compute_viewshed(dem, observer, observer_height_m=1.7, cell_size_m=30.0),
    repeats=3,
  )
  _time(
    "Baseline LOS",
    lambda: compute_viewshed_baseline(dem, observer, observer_height_m=1.7, cell_size_m=30.0),
    repeats=1,
  )


if __name__ == "__main__":
  main()
