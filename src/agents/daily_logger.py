import json
import os
from datetime import datetime
from pathlib import Path


class DailyLogger:
    """Simple logger that appends success and failure events by day."""

    def __init__(self, base_dir: str | os.PathLike | None = None):
        base = Path(base_dir) if base_dir is not None else Path(r"C:/Users/kanur/log")
        self.log_dir = base / "NOVA_LOGS"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _get_log_file(self, kind: str) -> Path:
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"trade_{kind}_{date_str}.json"
        return self.log_dir / filename

    def log_failure(self, agent: str, reason: str) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": agent,
            "action": "FAILURE",
            "reason": reason,
        }
        path = self._get_log_file("failures")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def log_success(
        self,
        agent: str,
        action: str,
        *,
        price: float,
        strategy: str,
        return_rate: float,
    ) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": agent,
            "action": action,
            "price": price,
            "strategy": strategy,
            "return_rate": round(return_rate, 4),
        }
        path = self._get_log_file("success")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
