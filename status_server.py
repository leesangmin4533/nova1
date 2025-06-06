from flask import Flask, jsonify, render_template
import threading

import log_analyzer


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
    def log_dashboard():
        logs = log_analyzer.load_logs()
        stats = log_analyzer.compute_statistics(logs)
        recent = logs[-10:]
        return render_template(
            "log_dashboard.html",
            stats=stats,
            recent_logs=recent,
        )

    thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread
