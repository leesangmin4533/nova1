from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple


def load_logs(log_dir: str = "log") -> List[dict]:
    """Load all ``*.json`` files from ``log_dir``.

    Returns a list of log entries sorted by timestamp when available."""
    path = Path(log_dir)
    logs: List[dict] = []
    if not path.is_dir():
        return logs

    for file in sorted(path.glob("*.json")):
        try:
            with open(file, "r", encoding="utf-8") as f:
                entry = json.load(f)
                logs.append(entry)
        except Exception:
            continue

    try:
        logs.sort(key=lambda x: x.get("timestamp", ""))
    except Exception:
        pass
    return logs


def analyze_logs(logs: List[dict]) -> Dict[str, object]:
    """Compute basic statistics from log entries."""
    stats: Dict[str, object] = {}

    total = len(logs)
    agent_counts: Dict[str, int] = defaultdict(int)
    returns: List[float] = []
    cumulative = 0.0
    strategy_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"wins": 0, "total": 0})

    for entry in logs:
        agent = entry.get("agent")
        if agent:
            agent_counts[agent] += 1

        rr = entry.get("return_rate")
        if isinstance(rr, (int, float)):
            returns.append(rr)
            cumulative += rr

        if entry.get("action") == "SELL":
            strat = entry.get("strategy")
            if strat:
                strategy_stats[strat]["total"] += 1
                if isinstance(rr, (int, float)) and rr > 0:
                    strategy_stats[strat]["wins"] += 1

    avg_return = sum(returns) / len(returns) if returns else 0.0
    max_return = max(returns) if returns else 0.0
    min_return = min(returns) if returns else 0.0

    win_rates = {
        name: (val["wins"] / val["total"] if val["total"] > 0 else 0.0)
        for name, val in strategy_stats.items()
    }

    stats["total_trades"] = total
    stats["agent_counts"] = dict(agent_counts)
    stats["average_return"] = avg_return
    stats["cumulative_return"] = cumulative
    stats["max_return"] = max_return
    stats["min_return"] = min_return
    stats["strategy_win_rates"] = win_rates

    return stats


def get_recent_logs(logs: List[dict], n: int = 10) -> List[dict]:
    """Return the ``n`` most recent log entries."""
    return logs[-n:]


def trade_returns(logs: List[dict]) -> Tuple[List[float], List[float]]:
    """Return per-trade returns and cumulative performance."""
    returns: List[float] = []
    cumulative: List[float] = []
    total = 0.0
    for entry in logs:
        rr = entry.get("return_rate")
        if isinstance(rr, (int, float)) and entry.get("action") in {"SELL", "CLOSE"}:
            returns.append(rr)
            total += rr
            cumulative.append(total)
    return returns, cumulative
