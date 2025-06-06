from flask import Flask, jsonify, render_template
import threading
from log_analyzer import (
    load_logs,
    analyze_logs,
    get_recent_logs,
    generate_bar_chart,
    generate_line_chart,
)


def start_status_server(trading_app, host="0.0.0.0", port=5000):
    """Start a background Flask server exposing current trading status."""

    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.route("/status")
    def status():
        if hasattr(trading_app, "visualizer"):
            return jsonify(trading_app.visualizer.state)
        return jsonify({})

    @app.route("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/log")
    def log_view():
        logs = load_logs("log")
        stats = analyze_logs(logs)
        recent = get_recent_logs(logs, 10)
        bar_chart = generate_bar_chart(stats.get("strategy_returns", {}))
        line_chart = generate_line_chart(stats.get("cumulative_curve", []))
        return render_template(
            "log_dashboard.html",
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
