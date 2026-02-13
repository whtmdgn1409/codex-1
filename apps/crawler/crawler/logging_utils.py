from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def log_event(level: str, event: str, **context: Any) -> None:
    payload: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "event": event,
    }
    if context:
        payload["context"] = context
    print(json.dumps(payload, ensure_ascii=False))
