from datetime import datetime, timedelta
from .strategy_scorer import StrategyScorer
from .news_adjuster import news_adjuster


class EntryDecisionAgent:
    """Determine trade entry signals for various strategies."""

    def __init__(self, adjuster=None):
        self.last_score_percent = 0.0
        self.scorer = StrategyScorer()
        self.adjuster = adjuster if adjuster is not None else news_adjuster
        self.nearest_failed = None
        self.failed_conditions = []
        self.override_rules = {
            "orderbook_bias_up": {
                "score_threshold": 70,
                "reason": "high_score_override",
            }
        }
        self.decision_history = []
        self.last_conflict = {"conflict_index": 0.0, "conflict_factors": []}

    def normalize_orderbook_strength(self, bids, asks):
        """Return normalized strength score from orderbook price-volume lists."""
        bid_strength = sum(b.get("price", 0) * b.get("volume", 0) for b in bids)
        ask_strength = sum(a.get("price", 0) * a.get("volume", 0) for a in asks)
        total = bid_strength + ask_strength
        if total == 0:
            return 0.0
        return (bid_strength - ask_strength) / total

    def evaluate(
        self,
        strategy,
        chart_data,
        order_status,
        order_book=None,
        *,
        logger=None,
        symbol=None,
        emotion_index=None,
        emotion_ma=None,
        news_emotion=None,
    ):
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
        if len(chart_data) >= 15:
            rsi_prev = self._calc_rsi(chart_data[:-1])
        else:
            rsi_prev = rsi
        rsi_diff = rsi - rsi_prev
        buy_sens = 1.0
        sell_sens = 1.0
        if rsi_diff > 0:
            buy_sens += 1
        elif rsi_diff < 0:
            sell_sens += 1
        if (emotion_ma is not None and emotion_ma >= 0.3) or (
            news_emotion is not None and news_emotion >= 0.3
        ):
            buy_sens *= 1.1
        if emotion_ma is not None and emotion_ma <= -0.3:
            sell_sens *= 1.1

        ma_10 = sum(chart_data[-10:]) / 10
        ma_34 = sum(chart_data[-34:]) / 34 if len(chart_data) >= 34 else ma20

        volatility = 0.0
        bb_score_val = 0
        if len(chart_data) >= 20:
            mean20 = sum(chart_data[-20:]) / 20
            var20 = sum((c - mean20) ** 2 for c in chart_data[-20:]) / 20
            std20 = (var20 ** 0.5)
            volatility = std20 / mean20 if mean20 else 0.0
            upper = mean20 + 2 * std20
            lower = mean20 - 2 * std20
            if recent_close > upper:
                bb_score_val = 1
            elif recent_close < lower:
                bb_score_val = -1
        
        golden_cross = False
        if len(chart_data) >= 25:
            prev_ma20 = sum(chart_data[-21:-1]) / 20
            golden_cross = ma5 > ma20 and chart_data[-6] <= prev_ma20

        rsi_threshold = 48.0
        if self.adjuster.active:
            rsi_threshold += self.adjuster.adjustments.get("rsi_offset", 0)
        if emotion_index is not None:
            rsi_threshold += emotion_index * 5

        if order_book:
            bid_volume = order_book.get("bid_volume")
            ask_volume = order_book.get("ask_volume")
            if bid_volume is None or ask_volume is None:
                bid_volume = sum(b.get("volume", 0) for b in order_book.get("bids", []))
                ask_volume = sum(a.get("volume", 0) for a in order_book.get("asks", []))
        else:
            bid_volume = ask_volume = 0

        condition_scores = {
            "rsi_above_threshold": rsi > rsi_threshold,
            "ma_cross": ma_10 > ma_34,
            "golden_cross": golden_cross,
            "orderbook_bias_up": bid_volume > ask_volume,
            "orderbook_bias_down": ask_volume > bid_volume,
            "volatility_threshold": volatility < 0.02,
        }

        condition_details = {
            "rsi_above_threshold": {
                "value": rsi,
                "threshold": rsi_threshold,
                "diff": rsi - rsi_threshold,
                "passed": rsi > rsi_threshold,
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
                "value": bid_volume - ask_volume if order_book else None,
                "threshold": 0,
                "diff": bid_volume - ask_volume if order_book else float("inf"),
                "passed": bid_volume > ask_volume if order_book else False,
            },
            "orderbook_bias_down": {
                "value": ask_volume - bid_volume if order_book else None,
                "threshold": 0,
                "diff": ask_volume - bid_volume if order_book else float("inf"),
                "passed": ask_volume > bid_volume if order_book else False,
            },
            "volatility_threshold": {
                "value": volatility,
                "threshold": 0.02,
                "diff": volatility - 0.02,
                "passed": volatility < 0.02,
            },
        }

        rsi_score_val = 1 if rsi > rsi_threshold else -1 if rsi < rsi_threshold else 0
        bb_score = bb_score_val
        ob_down = condition_scores.get("orderbook_bias_down", False)
        ts_score_val = 0
        buy_score = (
            (1 if rsi_score_val > 0 else 0)
            + (1 if bb_score > 0 else 0)
            + (1 if condition_scores.get("orderbook_bias_up") else 0)
            + (1 if ts_score_val > 0 else 0)
        )
        sell_score = (
            (1 if rsi_score_val < 0 else 0)
            + (1 if bb_score < 0 else 0)
            + (1 if ob_down else 0)
            + (1 if ts_score_val < 0 else 0)
        )
        if emotion_ma is not None:
            if emotion_ma > 0:
                buy_score += emotion_ma
            elif emotion_ma < 0:
                sell_score += abs(emotion_ma)

        failed_conditions = {k: v for k, v in condition_details.items() if not v["passed"]}
        self.failed_conditions = list(failed_conditions)
        if failed_conditions:
            nearest_name, nearest_info = min(failed_conditions.items(), key=lambda x: abs(x[1]["diff"]))
            self.nearest_failed = {"condition": nearest_name, **nearest_info}
        else:
            self.nearest_failed = None

        self.last_score_percent = self.scorer.score(condition_scores)
        if self.adjuster.active:
            factor = 1 + self.adjuster.adjustments.get("decision_sensitivity", 0.0)
            self.last_score_percent *= factor
        if emotion_index is not None:
            self.last_score_percent *= 1 + emotion_index * 0.1
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

        signal = "HOLD"
        if name in ["momentum", "trend_follow"]:
            if golden_cross and rsi > rsi_threshold:
                signal = "BUY"
        elif name == "reversal" and recent_close < ma5:
            signal = "BUY"

        if name == "orderbook_weighted" and order_book:
            bids = order_book.get("bids") or []
            asks = order_book.get("asks") or []
            score = self.normalize_orderbook_strength(bids[:10], asks[:10])
            signal = "HOLD"
            if score > 0.3:
                signal = "BUY"
            elif score < -0.3:
                signal = "SELL"
            self._compute_conflict(condition_scores, rsi, rsi_threshold, chart_data, order_book, signal)
            ci = self.last_conflict.get("conflict_index", 0.0)
            diff = buy_sens * buy_score - sell_sens * sell_score
            if ci >= 0.5:
                if diff > 0:
                    signal = "BUY"
                elif diff < 0:
                    signal = "SELL"
                else:
                    signal = "HOLD"
            if abs(diff) >= 1.5:
                signal = "BUY" if diff > 0 else "SELL"
            return {
                "signal": signal,
                "confidence": score,
                "strategy": "orderbook_weighted",
                "score_percent": self.last_score_percent,
            }

        if name == "take_profit" and order_status and order_status.get("has_position"):
            if order_status.get("return_rate", 0) >= 0.05:
                signal = "SELL"

        self._compute_conflict(condition_scores, rsi, rsi_threshold, chart_data, order_book, signal)
        ci = self.last_conflict.get("conflict_index", 0.0)
        diff = buy_sens * buy_score - sell_sens * sell_score
        if ci >= 0.5:
            if diff > 0:
                signal = "BUY"
            elif diff < 0:
                signal = "SELL"
            else:
                signal = "HOLD"
        if abs(diff) >= 1.5:
            signal = "BUY" if diff > 0 else "SELL"
        return signal

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

    def _calc_macd(self, closes, fast=12, slow=26, signal=9):
        if len(closes) < slow + signal:
            return 0.0

        def ema(vals, period):
            k = 2 / (period + 1)
            ema_val = vals[0]
            for v in vals[1:]:
                ema_val = v * k + ema_val * (1 - k)
            return ema_val

        fast_list = []
        slow_list = []
        e_fast = closes[0]
        e_slow = closes[0]
        for price in closes:
            e_fast = price * (2 / (fast + 1)) + e_fast * (1 - 2 / (fast + 1))
            e_slow = price * (2 / (slow + 1)) + e_slow * (1 - 2 / (slow + 1))
            fast_list.append(e_fast)
            slow_list.append(e_slow)
        macd_list = [f - s for f, s in zip(fast_list, slow_list)]
        e_signal = macd_list[0]
        for m in macd_list:
            e_signal = m * (2 / (signal + 1)) + e_signal * (1 - 2 / (signal + 1))
        return macd_list[-1] - e_signal

    def _recent_flip(self, new_signal: str) -> bool:
        now = datetime.utcnow()
        self.decision_history.append((now, new_signal))
        cutoff = now - timedelta(minutes=5)
        self.decision_history = [(t, s) for t, s in self.decision_history if t >= cutoff]
        if len(self.decision_history) < 3:
            return False
        seq = [s for _, s in self.decision_history[-3:]]
        if seq == ["BUY", "HOLD", "SELL"] or seq == ["SELL", "HOLD", "BUY"]:
            return True
        return False

    def _compute_conflict(self, condition_scores, rsi, rsi_threshold, chart_data, order_book, signal) -> None:
        sell_conditions = {
            "rsi_below_45": rsi < 45,
            "ma_cross_down": not condition_scores.get("ma_cross", False),
            "orderbook_bias_down": (order_book.get("ask_volume", 0) > order_book.get("bid_volume", 0)) if order_book else False,
        }
        macd_hist = self._calc_macd(chart_data)
        index = 0.0
        factors = []
        if any(condition_scores.values()) and any(sell_conditions.values()):
            index += 0.5
            factors.append("매수조건 A + 매도조건 B")
        if (rsi > rsi_threshold and macd_hist < 0) or (rsi < 45 and macd_hist > 0):
            index += 0.3
            factors.append("RSI↑ + MACD↓" if rsi > rsi_threshold else "RSI↓ + MACD↑")
        if self._recent_flip(signal):
            index += 0.2
            factors.append("잦은 판단 변경")
        index = min(index, 1.0)
        self.last_conflict = {
            "conflict_index": round(index, 2),
            "conflict_factors": factors,
        }

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
