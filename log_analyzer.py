import json
from pathlib import Path
from typing import List, Dict

def load_logs(log_dir: str = "log") -> List[Dict]:
    """Load log entries from the given directory."""
    path = Path(log_dir)
    if not path.exists():
        return []
    logs = []
    for file in sorted(path.glob("*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                logs.append(json.load(f))
        except Exception:
            continue
    logs.sort(key=lambda x: x.get("timestamp", ""))
    return logs


def compute_statistics(logs: List[Dict]) -> Dict[str, List[float]]:
    """Compute per-trade returns and cumulative returns."""
    returns = []
    cumulative = []
    total = 1.0
    for entry in logs:
        rr = entry.get("return_rate")
        if rr is not None and entry.get("action") in {"SELL", "CLOSE"}:
            returns.append(rr)
            total *= 1 + rr
            cumulative.append(total - 1)
    return {"returns": returns, "cumulative": cumulative}
