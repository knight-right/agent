from __future__ import annotations

import json
from typing import Any


def to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def from_json(text: str | None) -> Any:
    if not text:
        return None
    return json.loads(text)
