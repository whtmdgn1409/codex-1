from __future__ import annotations

import json
from urllib.request import Request, urlopen

from crawler.config import load_alert_config
from crawler.logging_utils import log_event


def send_failure_alert(*, job_name: str, error: str, attempts: int) -> bool:
    config = load_alert_config()
    if not config.slack_webhook_url:
        log_event("WARNING", "batch.alert.skipped", job=job_name, reason="missing_webhook")
        return False

    payload = {
        "text": f"[EPL Batch Failure] job={job_name} attempts={attempts} error={error}",
    }
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        config.slack_webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=config.timeout_seconds) as response:
            status = int(getattr(response, "status", 200))
        ok = 200 <= status < 300
        if ok:
            log_event("INFO", "batch.alert.sent", job=job_name, attempts=attempts, status=status)
            return True
        log_event("ERROR", "batch.alert.failed", job=job_name, attempts=attempts, status=status)
        return False
    except Exception as exc:
        log_event("ERROR", "batch.alert.error", job=job_name, attempts=attempts, error=repr(exc))
        return False
