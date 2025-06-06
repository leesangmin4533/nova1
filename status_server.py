from flask import Flask, jsonify, render_template
import threading


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

    thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread
