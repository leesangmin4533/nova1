"""Market sentiment classification agent."""

from __future__ import annotations

from typing import Dict, List

import numpy as np


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self) -> None:
        self.state: str = "NEUTRAL"

    def _rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        deltas = np.diff(closes[-(period + 1) :])
        gains = np.clip(deltas, 0, None).sum()
        losses = np.abs(np.clip(deltas, None, 0)).sum()
        if losses == 0:
            return 100.0
        rs = gains / losses
        return 100 - 100 / (1 + rs)

    def update(
        self,
        candle_data: Dict[str, List[float]],
        order_book: Dict[str, float],
        trade_strength: float,
    ) -> str:
        """Update sentiment based on market data."""

        closes = candle_data.get("close", [])
        volumes = candle_data.get("volume", [])
        if len(closes) < 2 or len(volumes) < 2:
            return self.state

        volume_rate = (volumes[-1] - volumes[-2]) / volumes[-2]
        rsi_val = self._rsi(closes)
        bid = order_book.get("bid", 0)
        ask = order_book.get("ask", 0)
        book_ratio = bid / (bid + ask) if (bid + ask) != 0 else 0.5

        window = closes[-20:]
        ma = float(np.mean(window))
        std = float(np.std(window))
        price = closes[-1]
        if price > ma + 2 * std:
            bb_signal = 1
        elif price < ma - 2 * std:
            bb_signal = -1
        else:
            bb_signal = 0

        score = 0
        score += 1 if volume_rate > 0 else -1
        score += 1 if rsi_val > 70 else -1 if rsi_val < 30 else 0
        score += 1 if book_ratio > 0.6 else -1 if book_ratio < 0.4 else 0
        score += bb_signal

        if score >= 3:
            self.state = self.LEVELS[4]
        elif score >= 2:
            self.state = self.LEVELS[3]
        elif score <= -3:
            self.state = self.LEVELS[0]
        elif score <= -2:
            self.state = self.LEVELS[1]
        else:
            self.state = self.LEVELS[2]
        return self.state
