from __future__ import annotations

from abc import ABC, abstractmethod

from app.dem.types import DemResult


class DemProvider(ABC):
  @abstractmethod
  def get_dem(
    self,
    observer_lat: float,
    observer_lon: float,
    radius_km: float,
    resolution_m: float,
  ) -> DemResult:
    raise NotImplementedError
