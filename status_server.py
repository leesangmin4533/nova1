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
    "rsi": None,
    "bb_score": None,
    "ts_score": None,
    "return_rate": None,
    "cumulative_return": 0.0,
    "last_trade_time": None,
    "positions": [],
    "bids": [],
    "asks": [],
    "buy_count": 0,
    "sell_count": 0,
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

