import math
from typing import List, Optional

from .utils import get_upbit_candles


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    def _calc_rsi(self, closes: List[float], period: int = 20) -> float:
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
        """Update sentiment based on market data from Upbit."""

        if candle_data is None:
            try:
                candle_data = get_upbit_candles()
            except Exception:
                return self.state

        rsi = self._calc_rsi(candle_data, period=20)

        if rsi < 30:
            level = 0
        elif rsi < 45:
            level = 1
        elif rsi < 55:
            level = 2
        elif rsi < 70:
            level = 3
        else:
            level = 4

        self.state = self.LEVELS[level]
        return self.state
