from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_REPO_ROOT = Path(__file__).resolve().parents[3]
_DATA_DIR = _REPO_ROOT / "data"


def load_json(filename: str) -> Any:
    path = _DATA_DIR / filename
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
