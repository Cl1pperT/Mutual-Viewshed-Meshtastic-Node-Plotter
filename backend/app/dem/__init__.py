from __future__ import annotations

from pathlib import Path

from app.dem.providers.base import DemProvider
from app.dem.providers.terrarium import TerrariumProvider
from app.dem.types import DemResult

DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[2] / "data" / "dem"


def get_dem(
  observer_lat: float,
  observer_lon: float,
  radius_km: float,
  resolution_m: float,
  provider: DemProvider | None = None,
  cache_dir: Path | None = None,
) -> DemResult:
  if provider is None:
    cache_root = cache_dir or DEFAULT_CACHE_DIR
    provider = TerrariumProvider(cache_root)

  return provider.get_dem(
    observer_lat=observer_lat,
    observer_lon=observer_lon,
    radius_km=radius_km,
    resolution_m=resolution_m,
  )
