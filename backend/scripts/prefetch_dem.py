#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from dataclasses import asdict

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.dem.providers.terrarium import TerrariumProvider

# Utah state bounding box (approximate state extremes in degrees).
UTAH_BBOX = {
  "min_lat": 37.0,
  "min_lon": -114.05,
  "max_lat": 42.0,
  "max_lon": -109.0,
}

PRESETS = {
  "fast": 90.0,
  "medium": 60.0,
  "high": 30.0,
}


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description="Prefetch Terrarium DEM tiles for a bounding box.")
  parser.add_argument("--min-lat", type=float, help="Minimum latitude")
  parser.add_argument("--min-lon", type=float, help="Minimum longitude")
  parser.add_argument("--max-lat", type=float, help="Maximum latitude")
  parser.add_argument("--max-lon", type=float, help="Maximum longitude")
  parser.add_argument(
    "--preset",
    choices=sorted(PRESETS.keys()),
    default="fast",
    help="Resolution preset (meters)",
  )
  parser.add_argument("--resolution-m", type=float, help="Resolution in meters per cell (overrides preset)")
  parser.add_argument(
    "--state",
    choices=["utah"],
    default="utah",
    help="Prefetch preset bounding box (currently only Utah)",
  )
  return parser.parse_args()


def main() -> None:
  args = parse_args()

  if args.min_lat is None or args.min_lon is None or args.max_lat is None or args.max_lon is None:
    if args.state == "utah":
      min_lat = UTAH_BBOX["min_lat"]
      min_lon = UTAH_BBOX["min_lon"]
      max_lat = UTAH_BBOX["max_lat"]
      max_lon = UTAH_BBOX["max_lon"]
    else:
      raise SystemExit("Missing bounding box. Provide --min-lat/--min-lon/--max-lat/--max-lon.")
  else:
    min_lat = args.min_lat
    min_lon = args.min_lon
    max_lat = args.max_lat
    max_lon = args.max_lon

  resolution_m = float(args.resolution_m) if args.resolution_m else PRESETS[args.preset]

  # The provider expects an explicit cache dir; use the default from the DEM module.
  from app.dem import DEFAULT_CACHE_DIR

  provider = TerrariumProvider(cache_dir=DEFAULT_CACHE_DIR)

  stats = provider.prefetch_bbox(
    min_lat=min_lat,
    min_lon=min_lon,
    max_lat=max_lat,
    max_lon=max_lon,
    resolution_m=resolution_m,
  )

  print("Prefetch complete:")
  for key, value in asdict(stats).items():
    print(f"  {key}: {value}")


if __name__ == "__main__":
  main()
