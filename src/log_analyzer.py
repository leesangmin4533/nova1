from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


def analyze_logs(log_dir: str) -> Dict[str, float]:
    """Analyze log files in ``log_dir`` and return basic performance metrics.

    Metrics include the number of buy and sell actions, the average return,
    cumulative return, and win rate. Log files are expected to be JSON files
    produced by ``LoggerAgent``.
    """
    path = Path(log_dir)
    buys = 0
    sells = 0
    returns = []

    for file in path.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
        action = str(data.get("action", "")).upper()
        if action == "BUY":
            buys += 1
        elif action in {"SELL", "CLOSE"}:
            sells += 1
        if action in {"SELL", "CLOSE"}:
            ret = data.get("return_rate")
            if isinstance(ret, (int, float)):
                returns.append(float(ret))

    avg_return = sum(returns) / len(returns) if returns else 0.0
    cumulative = 1.0
    for r in returns:
        cumulative *= 1 + r
    cumulative_return = cumulative - 1
    win_rate = (
        sum(1 for r in returns if r > 0) / len(returns) if returns else 0.0
    )

    return {
        "buys": buys,
        "sells": sells,
        "average_return": avg_return,
        "cumulative_return": cumulative_return,
        "win_rate": win_rate,
    }

