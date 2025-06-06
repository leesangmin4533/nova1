from flask import Flask, jsonify, render_template
import threading
from log_analyzer import (
    load_logs,
    analyze_logs,
    get_recent_logs,
    generate_bar_chart,
    generate_line_chart,
)

state_store = {
    "sentiment": "NEUTRAL",
    "strategy": None,
    "position": None,
    "signal": "HOLD",
    "price": None,
    "balance": 0.0,
    "equity": 0.0,
}


def update_state(**kwargs):
    """Merge ``kwargs`` into the global ``state_store`` and recompute equity."""
    state_store.update(kwargs)
    equity = state_store.get("balance", 0.0)
    price = state_store.get("price")
    pos = state_store.get("position")
    if pos and price is not None:
        equity += price * pos.get("quantity", 1.0)
    state_store["equity"] = equity


def start_status_server(host: str = "0.0.0.0", port: int = 5000):
    """Start a background Flask server exposing current trading status."""

    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.route("/api/status")
    def api_status():
        return jsonify(state_store)

    @app.route("/")
    def dashboard():
        return render_template("status.html")

    @app.route("/log")
    def log_view():
        logs = load_logs("log")
        stats = analyze_logs(logs)
        recent = get_recent_logs(logs, 10)
        bar_chart = generate_bar_chart(stats.get("strategy_returns", {}))
        line_chart = generate_line_chart(stats.get("cumulative_curve", []))
        return render_template(
            "log.html",
            stats=stats,
            bar_chart=bar_chart,
            line_chart=line_chart,
            recent=recent,
        )

    thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread
