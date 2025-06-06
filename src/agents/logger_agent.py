import json
from pathlib import Path
from datetime import datetime


class LoggerAgent:
    """Log actions and agent outputs to JSON files."""

    def __init__(self, log_dir="log"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.last_log = None

    def log(
        self,
        agent,
        action,
        price=None,
        confidence=None,
        symbol=None,
        return_rate=None,
    ):
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "agent": agent,
            "action": action,
            "price": price,
            "confidence": confidence,
            "symbol": symbol,
            "return_rate": return_rate,
        }

        compare = {
            "agent": agent,
            "action": action,
            "price": price,
            "symbol": symbol,
            "return_rate": return_rate,
        }
        if self.last_log and all(compare.get(k) == self.last_log.get(k) for k in compare):
            return None

        self.last_log = compare

        filename = self.log_dir / f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S%f')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        return timestamp

