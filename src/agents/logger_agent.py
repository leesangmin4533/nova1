import json
from pathlib import Path
from datetime import datetime


class LoggerAgent:
    """Log actions and agent outputs to JSON files."""

    def __init__(self, log_dir="log"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, agent, action, price=None, confidence=None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent,
            "action": action,
            "price": price,
            "confidence": confidence,
        }
        filename = self.log_dir / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S%f')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
