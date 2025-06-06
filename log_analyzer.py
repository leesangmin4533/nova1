from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import io
import base64


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
    """Compute statistics from log entries.

    Fields required by unit tests are preserved while additional metrics
    useful for visualisation are also returned.
    """

    stats: Dict[str, object] = {}

    trade_actions = 0
    agent_counts: Dict[str, int] = defaultdict(int)
    strategy_counts: Dict[str, int] = defaultdict(int)

    returns: List[float] = []
    cumulative = 0.0
    cumulative_curve: List[Tuple[str, float]] = []

    strategy_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"wins": 0, "total": 0})
    strategy_returns: Dict[str, List[float]] = defaultdict(list)

    for entry in logs:
        agent = entry.get("agent")
        if agent:
            agent_counts[agent] += 1

        action = entry.get("action")
        if action in {"BUY", "SELL"}:
            trade_actions += 1
            strat = entry.get("strategy")
            if strat:
                strategy_counts[strat] += 1

        rr = entry.get("return_rate")
        if isinstance(rr, (int, float)):
            returns.append(rr)
            cumulative += rr

            if action in {"SELL", "CLOSE"}:
                strat = entry.get("strategy")
                if strat:
                    strategy_returns[strat].append(rr)

        if action == "SELL":
            strat = entry.get("strategy")
            if strat:
                strategy_stats[strat]["total"] += 1
                if isinstance(rr, (int, float)) and rr > 0:
                    strategy_stats[strat]["wins"] += 1

        cumulative_curve.append((entry.get("timestamp"), cumulative))

    avg_return = sum(returns) / len(returns) if returns else 0.0
    max_return = max(returns) if returns else 0.0
    min_return = min(returns) if returns else 0.0

    win_rates = {
        name: (val["wins"] / val["total"] if val["total"] > 0 else 0.0)
        for name, val in strategy_stats.items()
    }

    avg_strategy_returns = {
        name: (sum(vals) / len(vals) if vals else 0.0)
        for name, vals in strategy_returns.items()
    }

    stats.update(
        {
            "total_trades": len(logs),
            "trade_actions": trade_actions,
            "agent_counts": dict(agent_counts),
            "strategy_counts": dict(strategy_counts),
            "average_return": avg_return,
            "cumulative_return": cumulative,
            "max_return": max_return,
            "min_return": min_return,
            "strategy_win_rates": win_rates,
            "strategy_returns": avg_strategy_returns,
            "cumulative_curve": cumulative_curve,
        }
    )

    return stats


def get_recent_logs(logs: List[dict], n: int = 10) -> List[dict]:
    """Return the ``n`` most recent log entries."""
    return logs[-n:]


def generate_bar_chart(data: Dict[str, float]) -> str:
    """Return a base64 PNG bar chart for the given mapping."""
    if not data:
        return ""
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.bar(list(data.keys()), list(data.values()))
    ax.set_ylabel("Return")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def generate_line_chart(curve: List[Tuple[str, float]]) -> str:
    """Return a base64 PNG line chart from cumulative return curve."""
    if not curve:
        return ""
    x = list(range(len(curve)))
    y = [c[1] for c in curve]
    fig, ax = plt.subplots(figsize=(4, 3))
    ax.plot(x, y)
    ax.set_ylabel("Cumulative Return")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

