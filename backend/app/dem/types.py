from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from affine import Affine


@dataclass(frozen=True)
class DemResult:
  elevation: np.ndarray
  transform: Affine
  crs: str
  metadata: dict[str, Any] | None = None
