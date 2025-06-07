from flask import Flask, jsonify, render_template, request
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json

CONFIG_PATH = Path(r"C:/Users/kanur/log/설정/ui_config.json")


def load_ui_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"theme": "Dark Insight"}


def save_ui_config(theme: str) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {"theme": theme, "last_updated": datetime.now().strftime("%Y-%m-%dT%H:%M")},
            f,
            ensure_ascii=False,
        )

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
    "selected_strategy": None,
    "strategy_score": None,
    "position": None,
    "signal": "HOLD",
    "price": None,
    "balance": 0.0,
    "equity": 0.0,
    "weight": None,
    "weights": {},
    "bid_volume": None,
    "ask_volume": None,
    "orderbook_score": None,
    "classified_emotion": None,
    "emotion_index": None,
    "rsi": None,
    "bb_score": None,
    "ts_score": None,
    "nearest_failed": None,
    "return_rate": None,
    "cumulative_return": 0.0,
    "last_trade_time": None,
    "positions": [],
    "bids": [],
    "asks": [],
    "buy_count": 0,
    "sell_count": 0,
    "theme": load_ui_config().get("theme", "Dark Insight"),
    "decision": {},
}


def update_state(**kwargs):
    """Merge ``kwargs`` into the global ``state_store`` and recompute equity."""
    bids = kwargs.get("bids")
    asks = kwargs.get("asks")

    if bids is not None:
        filtered = []
        seen = set()
        for price, vol in bids:
            if not vol:
                continue
            key = (price, vol)
            if key in seen:
                continue
            seen.add(key)
            filtered.append([price, vol])
        kwargs["bids"] = filtered

    if asks is not None:
        filtered = []
        seen = set()
        for price, vol in asks:
            if not vol:
                continue
            key = (price, vol)
            if key in seen:
                continue
            seen.add(key)
            filtered.append([price, vol])
        kwargs["asks"] = filtered

    state_store.update(kwargs)
    equity = state_store.get("balance", 0.0)
    price = state_store.get("price")
    positions = state_store.get("positions", [])
    if positions and price is not None:
        for pos in positions:
            equity += price * pos.get("quantity", 1.0)
    state_store["equity"] = equity


def start_status_server(host: str = "0.0.0.0", port: int = 5000, *, position_manager=None, logger_agent=None):
    """Start a background Flask server exposing current trading status."""

    app = Flask(__name__, static_folder="static", template_folder="templates")

    @app.route("/api/status")
    def api_status():
        status = dict(state_store)
        if position_manager is not None:
            status["buy_count"] = position_manager.total_buys
            status["sell_count"] = position_manager.total_sells
        if logger_agent is not None:
            try:
                status["recent_trades"] = logger_agent.get_recent_trades(limit=10)
            except Exception:
                status["recent_trades"] = []
        return jsonify(status)

    @app.route("/api/theme", methods=["GET", "POST"])
    def api_theme():
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
            theme = data.get("theme")
            if theme:
                state_store["theme"] = theme
                save_ui_config(theme)
            return jsonify({"theme": state_store.get("theme")})
        return jsonify({"theme": state_store.get("theme")})

    @app.route("/")
    def dashboard():
        return render_template("nova_decision.html")

    @app.route("/api/decision")
    def api_decision():
        data = state_store.get("decision", {})
        if not data:
            decision_path = Path(r"C:/Users/kanur/log/판단/latest_decision.json")
            try:
                if decision_path.exists():
                    with open(decision_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
            except Exception:
                data = {}
        return jsonify(data)

    @app.route("/log")
    def log_view():
        logs = load_logs("log")
        stats = analyze_logs(logs)
        recent = []
        for l in get_recent_logs(logs, 10):
            ts = l.get("timestamp")
            try:
                dt = datetime.fromisoformat(ts)
                kst = dt + timedelta(hours=9)
                l = dict(l)
                l["timestamp"] = kst.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass
            recent.append(l)
        bar_chart = generate_bar_chart(stats.get("strategy_returns", {}))
        line_chart = generate_line_chart(stats.get("cumulative_curve", []))
        score_vals = [l.get("score_percent") for l in logs if l.get("type") == "condition_evaluation"]
        avg_score = sum(score_vals) / len(score_vals) if score_vals else 0.0
        reason_stats = {}
        for l in logs:
            if l.get("type") == "entry_denied":
                r = l.get("reason")
                reason_stats[r] = reason_stats.get(r, 0) + 1
        return render_template(
            "log.html",
            stats=stats,
            bar_chart=bar_chart,
            line_chart=line_chart,
            recent=recent,
            average_score=avg_score,
            reason_stats=reason_stats,
        )

    thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, use_reloader=False),
        daemon=True,
    )
    thread.start()
    return thread

