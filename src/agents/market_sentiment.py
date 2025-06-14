import json
import math
from pathlib import Path
from config import LOG_BASE_DIR
from datetime import datetime
from typing import List, Optional

from .utils import get_upbit_candles


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"
        self.rsi = 50.0
        self.bb_score = 0
        self.ts_score = 0
        self.emotion_index = 0.0
        self.applied_emotion_index = 0.0
        self.ma_3d = 0.0
        self.classified_emotion = "무관심"

    def calc_rsi(self, closes: List[float], period: int = 20) -> float:
        """Return the Relative Strength Index (RSI) for the given closes.

        If the number of closes is insufficient for the desired period, a
        neutral value of ``50.0`` is returned. When the average loss is ``0``,
        the function returns ``100.0`` as the RSI cannot be computed.

        Args:
            closes: Sequence of closing prices in chronological order.
            period: Number of periods to use for the RSI calculation.

        Returns:
            Calculated RSI value in the range ``0.0`` to ``100.0``.
        """

        if len(closes) < period + 1:
            return 50.0

        gains: List[float] = []
        losses: List[float] = []
        for i in range(1, period + 1):
            diff = closes[-i] - closes[-i - 1]
            if diff > 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if math.isclose(avg_loss, 0):
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def update(
        self,
        candle_data: Optional[List[float]] = None,
        order_book=None,
        trade_strength=None,
    ) -> str:
        """Update sentiment using RSI, order book and Bollinger Bands."""

        if candle_data is None:
            try:
                candle_data = get_upbit_candles()
            except Exception:
                return self.state

        rsi = self.calc_rsi(candle_data, period=20)
        self.rsi = rsi

        if len(candle_data) >= 20:
            ma = sum(candle_data[-20:]) / 20
            variance = sum((c - ma) ** 2 for c in candle_data[-20:]) / 20
            stddev = math.sqrt(variance)
            upper = ma + 2 * stddev
            lower = ma - 2 * stddev
            price = candle_data[-1]
            bb_score = 1 if price > upper else -1 if price < lower else 0
        else:
            bb_score = 0
        self.bb_score = bb_score

        ob_score = 0
        if order_book and isinstance(order_book, dict):
            bid = order_book.get("bid_volume", 0)
            ask = order_book.get("ask_volume", 0)
            total = bid + ask
            if total > 0:
                ratio = (bid - ask) / total
                if ratio > 0.6:
                    ob_score = 1
                elif ratio < -0.6:
                    ob_score = -1

        ts_score = 0
        if trade_strength is not None:
            if trade_strength > 1.1:
                ts_score = 1
            elif trade_strength < 0.9:
                ts_score = -1
        self.ts_score = ts_score

        score = 0
        if rsi > 70:
            score += 2
        elif rsi > 55:
            score += 1
        elif rsi < 30:
            score -= 2
        elif rsi < 45:
            score -= 1

        score += bb_score + ob_score + ts_score

        if score <= -2:
            level = 0
        elif score == -1:
            level = 1
        elif score == 0:
            level = 2
        elif score == 1:
            level = 3
        else:
            level = 4

        self.state = self.LEVELS[level]
        self.classified_emotion = {
            "EXTREME_FEAR": "공포",
            "FEAR": "공포",
            "NEUTRAL": "무관심",
            "GREED": "기대",
            "EXTREME_GREED": "기대",
        }[self.state]
        self.emotion_index = {
            "EXTREME_FEAR": -1.0,
            "FEAR": -0.5,
            "NEUTRAL": 0.0,
            "GREED": 0.5,
            "EXTREME_GREED": 1.0,
        }[self.state]
        self._update_ma()
        return self.state

    # --------------------------------------------------------------
    def _update_ma(self) -> None:
        """Update 3-day moving average of emotion index."""
        path = LOG_BASE_DIR / "감정지수" / "emotion_MA.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
        history = data.get("history", [])
        today = datetime.utcnow().strftime("%Y-%m-%d")
        found = False
        for h in history:
            if h.get("date") == today:
                h["index"] = self.emotion_index
                found = True
                break
        if not found:
            history.append({"date": today, "index": self.emotion_index})
        history = sorted(history, key=lambda x: x.get("date", ""))[-3:]
        ma = sum(h.get("index", 0.0) for h in history) / len(history)
        self.ma_3d = ma
        self.applied_emotion_index = self.emotion_index * 0.5 + ma * 0.5
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"history": history, "MA_3d": self.ma_3d, "applied_index": self.applied_emotion_index},
                f,
                ensure_ascii=False,
                indent=2,
            )
