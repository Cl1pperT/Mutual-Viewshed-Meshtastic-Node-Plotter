from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

SCENARIO_DIR = Path.home() / "Downloads" / "LocalViewshedExplorer" / "data" / "scenarios"
SCENARIO_FILE = SCENARIO_DIR / "scenarios.json"
SCENARIO_LOCK = Lock()


def list_scenarios() -> list[dict[str, Any]]:
  with SCENARIO_LOCK:
    items = _load_all()
  return sorted(items, key=lambda item: item.get("createdAt", ""), reverse=True)


def get_scenario(scenario_id: str) -> dict[str, Any] | None:
  with SCENARIO_LOCK:
    items = _load_all()
  for item in items:
    if item.get("id") == scenario_id:
      return item
  return None


def save_scenario(name: str, request: dict[str, Any]) -> dict[str, Any]:
  scenario = {
    "id": uuid4().hex,
    "name": name,
    "createdAt": datetime.now(timezone.utc).isoformat(),
    "request": request,
  }
  with SCENARIO_LOCK:
    items = _load_all()
    items.append(scenario)
    _write_all(items)
  return scenario


def delete_scenario(scenario_id: str) -> bool:
  with SCENARIO_LOCK:
    items = _load_all()
    filtered = [item for item in items if item.get("id") != scenario_id]
    if len(filtered) == len(items):
      return False
    _write_all(filtered)
  return True


def _load_all() -> list[dict[str, Any]]:
  if not SCENARIO_FILE.exists():
    return []
  try:
    return json.loads(SCENARIO_FILE.read_text())
  except Exception:
    return []


def _write_all(items: list[dict[str, Any]]) -> None:
  SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
  tmp_path = SCENARIO_FILE.with_suffix(".json.tmp")
  tmp_path.write_text(json.dumps(items, indent=2, sort_keys=True))
  tmp_path.replace(SCENARIO_FILE)
