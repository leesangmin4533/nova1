import json
from datetime import datetime
from pathlib import Path
from config import LOG_BASE_DIR


class SessionLogger:
    """Unified logger that appends entries to a single file per session."""

    def __init__(self, base_dir: str | Path | None = None):
        base = Path(base_dir) if base_dir is not None else LOG_BASE_DIR
        self.log_dir = base / "NOVA_LOGS"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"trade_log_{session_id}.json"

    def log_entry(self, data: dict) -> None:
        data = dict(data)
        data.setdefault("timestamp", datetime.now().isoformat(timespec="seconds"))
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def log_success(self, agent: str, action: str, *, price: float, strategy: str, return_rate: float) -> None:
        self.log_entry({
            "agent": agent,
            "action": action,
            "price": price,
            "strategy": strategy,
            "return_rate": round(return_rate, 4),
        })

    def log_failure(self, agent: str, reason: str) -> None:
        self.log_entry({
            "agent": agent,
            "action": "FAILURE",
            "reason": reason,
        })

    def log_hold(self, agent: str) -> None:
        self.log_entry({
            "agent": agent,
            "action": "HOLD",
        })

    def get_log_path(self) -> str:
        """Return the path to the session log file as a string."""
        return str(self.log_file)
