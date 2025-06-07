from .strategy_scorer import StrategyScorer


class EntryDecisionAgent:
    """Determine trade entry signals for various strategies."""

    def __init__(self):
        self.last_score_percent = 0.0
        self.scorer = StrategyScorer()
        self.nearest_failed = None
        self.failed_conditions = []
        self.override_rules = {
            "orderbook_bias_up": {
                "score_threshold": 70,
                "reason": "high_score_override",
            }
        }

    def normalize_orderbook_strength(self, bids, asks):
        """Return normalized strength score from orderbook price-volume lists."""
        bid_strength = sum(b.get("price", 0) * b.get("volume", 0) for b in bids)
        ask_strength = sum(a.get("price", 0) * a.get("volume", 0) for a in asks)
        total = bid_strength + ask_strength
        if total == 0:
            return 0.0
        return (bid_strength - ask_strength) / total

    def evaluate(self, strategy, chart_data, order_status, order_book=None, *, logger=None, symbol=None):
        """Return BUY, SELL, or HOLD signal or detailed dict for special strategy.

        When ``logger`` is provided, a ``condition_evaluation`` event will be written
        with detailed condition scores and the overall satisfaction percentage.
        The most recent percentage is stored in ``last_score_percent`` for external
        use.
        """
        name = strategy[0] if isinstance(strategy, tuple) else strategy
        if not chart_data or len(chart_data) < 20:
            self.last_score_percent = 0.0
            return "HOLD"

        recent_close = chart_data[-1]
        ma5 = sum(chart_data[-5:]) / 5
        ma20 = sum(chart_data[-20:]) / 20

        rsi = self._calc_rsi(chart_data)

        ma_10 = sum(chart_data[-10:]) / 10
        ma_34 = sum(chart_data[-34:]) / 34 if len(chart_data) >= 34 else ma20

        volatility = 0.0
        if len(chart_data) >= 20:
            mean20 = sum(chart_data[-20:]) / 20
            var20 = sum((c - mean20) ** 2 for c in chart_data[-20:]) / 20
            volatility = (var20 ** 0.5) / mean20 if mean20 else 0.0

        golden_cross = False
        if len(chart_data) >= 25:
            prev_ma20 = sum(chart_data[-21:-1]) / 20
            golden_cross = ma5 > ma20 and chart_data[-6] <= prev_ma20

        condition_scores = {
            "rsi_above_55": rsi > 55,
            "ma_cross": ma_10 > ma_34,
            "golden_cross": golden_cross,
            "orderbook_bias_up": (order_book.get("bid_volume", 0) > order_book.get("ask_volume", 0)) if order_book else False,
            "volatility_threshold": volatility < 0.02,
        }

        condition_details = {
            "rsi_above_55": {
                "value": rsi,
                "threshold": 55,
                "diff": rsi - 55,
                "passed": rsi > 55,
            },
            "ma_cross": {
                "value": ma_10 - ma_34,
                "threshold": 0,
                "diff": ma_10 - ma_34,
                "passed": ma_10 > ma_34,
            },
            "golden_cross": {
                "value": ma5 - ma20,
                "threshold": 0,
                "diff": ma5 - ma20,
                "passed": golden_cross,
            },
            "orderbook_bias_up": {
                "value": (order_book.get("bid_volume", 0) - order_book.get("ask_volume", 0)) if order_book else None,
                "threshold": 0,
                "diff": (order_book.get("bid_volume", 0) - order_book.get("ask_volume", 0)) if order_book else float("inf"),
                "passed": (order_book.get("bid_volume", 0) > order_book.get("ask_volume", 0)) if order_book else False,
            },
            "volatility_threshold": {
                "value": volatility,
                "threshold": 0.02,
                "diff": volatility - 0.02,
                "passed": volatility < 0.02,
            },
        }

        failed_conditions = {k: v for k, v in condition_details.items() if not v["passed"]}
        self.failed_conditions = list(failed_conditions)
        if failed_conditions:
            nearest_name, nearest_info = min(failed_conditions.items(), key=lambda x: abs(x[1]["diff"]))
            self.nearest_failed = {"condition": nearest_name, **nearest_info}
        else:
            self.nearest_failed = None

        self.last_score_percent = self.scorer.score(condition_scores)
        if failed_conditions:
            self.scorer.tune_weights(failed_conditions.keys())

        if logger is not None:
            logger.log_event({
                "type": "condition_evaluation",
                "symbol": symbol,
                "condition_scores": condition_scores,
                "condition_details": condition_details,
                "nearest_failed": self.nearest_failed,
                "score_percent": self.last_score_percent,
            })

        if name in ["momentum", "trend_follow"]:
            if golden_cross and rsi > 55:
                return "BUY"
        if name == "reversal" and recent_close < ma5:
            return "BUY"

        if name == "orderbook_weighted" and order_book:
            bids = order_book.get("bids") or []
            asks = order_book.get("asks") or []
            score = self.normalize_orderbook_strength(bids[:10], asks[:10])
            signal = "HOLD"
            if score > 0.3:
                signal = "BUY"
            elif score < -0.3:
                signal = "SELL"
            return {
                "signal": signal,
                "confidence": score,
                "strategy": "orderbook_weighted",
                "score_percent": self.last_score_percent,
            }

        if name == "take_profit" and order_status and order_status.get("has_position"):
            if order_status.get("return_rate", 0) >= 0.05:
                return "SELL"

        return "HOLD"

    def _calc_rsi(self, closes, period=14):
        if len(closes) < period + 1:
            return 50.0
        gains = []
        losses = []
        for i in range(1, period + 1):
            diff = closes[-i] - closes[-i - 1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def decide_entry(self, signal, reason, score_percent):
        """Return ``(allow, reason)`` applying override rules."""
        override_reason = None
        if signal == "BUY":
            for cond, cfg in self.override_rules.items():
                if score_percent >= cfg.get("score_threshold", 100) and cond in self.failed_conditions:
                    override_reason = cfg.get("reason")
                    break

        if override_reason:
            return True, override_reason

        allow_entry = signal == "BUY" and reason is None
        entry_reason = reason or "condition_failed"
        return allow_entry, entry_reason
