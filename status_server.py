from flask import Flask, jsonify
import threading


def start_status_server(trading_app, host="0.0.0.0", port=5000):
    """Start a background Flask server exposing current trading status."""

    app = Flask(__name__)

    @app.route("/status")
    def status():
        position = trading_app.position if getattr(trading_app, "position", None) else None
        return jsonify(
            sentiment=getattr(trading_app.sentiment_agent, "state", None),
            strategy=getattr(trading_app.strategy_selector, "current_strategy", None),
            position=position,
            signal=getattr(trading_app, "last_signal", None),
        )

    thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread
