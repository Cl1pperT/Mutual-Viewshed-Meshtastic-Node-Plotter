from __future__ import annotations

import math
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Local Viewshed Explorer API")

app.add_middleware(
  CORSMiddleware,
  allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
  ],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


class Observer(BaseModel):
  lat: float
  lon: float

  @field_validator("lat")
  @classmethod
  def validate_lat(cls, value: float) -> float:
    if not -90 <= value <= 90:
      raise ValueError("Latitude must be between -90 and 90.")
    return value

  @field_validator("lon")
  @classmethod
  def validate_lon(cls, value: float) -> float:
    if not -180 <= value <= 180:
      raise ValueError("Longitude must be between -180 and 180.")
    return value


class ViewshedRequest(BaseModel):
  observer: Observer
  observerHeightM: float = Field(gt=0)
  maxRadiusKm: float = Field(gt=0)
  resolutionM: float = Field(gt=0)


class ViewshedResponse(BaseModel):
  observer: Observer
  maxRadiusKm: float
  polygon: dict[str, Any]


def build_circle_polygon(lat: float, lon: float, radius_km: float, points: int = 64) -> dict[str, Any]:
  lat_rad = math.radians(lat)
  km_per_deg_lat = 110.574
  km_per_deg_lon = max(111.320 * math.cos(lat_rad), 1e-6)
  coords: list[list[float]] = []

  for i in range(points + 1):
    angle = 2 * math.pi * i / points
    dlat = (radius_km * math.sin(angle)) / km_per_deg_lat
    dlon = (radius_km * math.cos(angle)) / km_per_deg_lon
    coords.append([lon + dlon, lat + dlat])

  return {
    "type": "Polygon",
    "coordinates": [coords],
  }


@app.get("/health")
def health_check() -> dict:
  return {"status": "ok"}


@app.post("/viewshed", response_model=ViewshedResponse)
def compute_viewshed(payload: ViewshedRequest) -> ViewshedResponse:
  polygon = build_circle_polygon(
    lat=payload.observer.lat,
    lon=payload.observer.lon,
    radius_km=payload.maxRadiusKm,
  )

  return ViewshedResponse(
    observer=payload.observer,
    maxRadiusKm=payload.maxRadiusKm,
    polygon=polygon,
  )
