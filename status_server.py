from flask import Flask, render_template_string
import json
from pathlib import Path
from datetime import datetime

# shared state updated by main.py
shared_state = {
    "sentiment": "NEUTRAL",
    "strategy": ("none", {}),
    "signal": "HOLD",
    "positions": []
}

HTML_TEMPLATE = """
<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<title>Trading Agent Status</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
<meta http-equiv="refresh" content="3">
</head>
<body class='container mt-4'>
<h1 class='mb-4'>Trading Agent Status</h1>
<p><strong>Current Time:</strong> {{ now }}</p>
<ul class='list-group'>
  <li class='list-group-item'><strong>Sentiment:</strong> {{ sentiment }}</li>
  <li class='list-group-item'><strong>Strategy:</strong> {{ strategy_id }} {{ params }}</li>
  <li class='list-group-item'><strong>Last Signal:</strong> {{ signal }}</li>
  <li class='list-group-item'><strong>Positions:</strong> {{ positions }}</li>
</ul>
<h3 class='mt-4'>Recent Logs</h3>
<ul class='list-group'>
  {% for log in logs %}
  <li class='list-group-item'>{{ log['timestamp'] }} - {{ log['agent'] }} - {{ log['action'] }}</li>
  {% endfor %}
</ul>
</body>
</html>
"""


def load_recent_logs(log_dir="log", limit=5):
    path = Path(log_dir)
    files = sorted(path.glob("*.json"), reverse=True)[:limit]
    logs = []
    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                logs.append(json.load(f))
        except Exception:
            continue
    return logs


def create_app():
    app = Flask(__name__)

    @app.route("/status")
    def status():
        logs = load_recent_logs()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        strategy_id, params = shared_state.get("strategy", ("none", {}))
        return render_template_string(
            HTML_TEMPLATE,
            now=now,
            sentiment=shared_state.get("sentiment"),
            strategy_id=strategy_id,
            params=params,
            signal=shared_state.get("signal"),
            positions=shared_state.get("positions"),
            logs=logs,
        )

    return app
