# -*- coding: utf-8 -*-
"""Simple Flask server for viewing recent session logs."""

from flask import Flask, render_template_string
import json
from pathlib import Path

app = Flask(__name__)


@app.route("/report")
def report():
    """Return an HTML summary of the latest session log."""
    log_dir = Path.home() / "Desktop" / "NOVA_LOGS"
    files = sorted(log_dir.glob("session_log_*.json"), reverse=True)
    if not files:
        return "\u274c \ub85c\uadf8 \ud30c\uc77c\uc774 \uc5c6\uc2b5\ub2c8\ub2e4."  # '❌ 로그 파일이 없습니다.'

    latest = files[0]
    with open(latest, encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]

    stats = {"BUY": 0, "SELL": 0, "FAILURE": 0, "HOLD": 0}
    strategy_returns = {}

    for entry in lines:
        action = entry.get("action")
        stats[action] = stats.get(action, 0) + 1
        if action == "SELL":
            strategy = entry.get("strategy", "unknown")
            ret = entry.get("return_rate", 0)
            strategy_returns.setdefault(strategy, []).append(ret)

    strategy_summary = {
        k: round(sum(v) / len(v) * 100, 2) for k, v in strategy_returns.items()
    }

    html = """
    <h1>NOVA \uace0\ub824 \ub9ac\ud3ec\ud2b8</h1>
    <h3>\ucd5c\uadfc \uc138\uc158: {{ filename }}</h3>
    <p>\ucd1d \ub85c\uadf8 \uc218: {{ total }}</p>
    <ul>
      {% for k, v in stats.items() %}
        <li>{{ k }}: {{ v }}</li>
      {% endfor %}
    </ul>
    <h3>\uc804\ub7b5\ubcc4 \ud3c9\uade0 \uc218\uc775\ub960</h3>
    <ul>
      {% for k, v in strategy_summary.items() %}
        <li>{{ k }}: {{ v }}%</li>
      {% endfor %}
    </ul>
    """

    return render_template_string(
        html,
        filename=latest.name,
        total=len(lines),
        stats=stats,
        strategy_summary=strategy_summary,
    )


if __name__ == "__main__":
    app.run(port=7860)
