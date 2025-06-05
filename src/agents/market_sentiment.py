"""Market sentiment classifier."""

from __future__ import annotations

import time
from typing import Iterable, Mapping


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self, rsi_period: int = 14, bollinger_period: int = 20) -> None:
        self.state = "NEUTRAL"
        self.last_update = 0.0
        self.rsi_period = rsi_period
        self.bollinger_period = bollinger_period

    @staticmethod
    def _rsi(prices: Iterable[float], period: int) -> float:
        """Return RSI for the given price list."""
        prices = list(prices)
        if len(prices) <= period:
            return 50.0
        gains = []
        losses = []
        for i in range(1, period + 1):
            diff = prices[-i] - prices[-i - 1]
            if diff >= 0:
                gains.append(diff)
            else:
                losses.append(abs(diff))
        avg_gain = sum(gains) / period if gains else 0.0
        avg_loss = sum(losses) / period if losses else 1e-9
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def update(
        self,
        candle_data: Iterable[Mapping[str, float]] | None,
        order_book: Mapping[str, float] | None,
        trade_strength: float | None,
    ) -> str:
        """Update sentiment based on market data every minute."""

        now = time.time()
        if now - self.last_update < 60:
            return self.state
        self.last_update = now

        prices = [c.get("close", 0.0) for c in candle_data or []]
        volumes = [c.get("volume", 0.0) for c in candle_data or []]

        rsi = self._rsi(prices, self.rsi_period)

        if len(prices) >= self.bollinger_period:
            recent = prices[-self.bollinger_period :]
        else:
            recent = prices
        mean = sum(recent) / len(recent) if recent else 0.0
        variance = sum((p - mean) ** 2 for p in recent) / len(recent) if recent else 0.0
        std = variance ** 0.5
        upper_band = mean + 2 * std
        lower_band = mean - 2 * std
        last_price = prices[-1] if prices else 0.0

        vol_change = 0.0
        if len(volumes) >= 2 and volumes[-2] > 0:
            vol_change = (volumes[-1] - volumes[-2]) / volumes[-2]

        bid = (order_book or {}).get("bid", 0.0)
        ask = (order_book or {}).get("ask", 0.0)
        book_ratio = bid / (bid + ask) if bid + ask > 0 else 0.5
        strength = trade_strength if trade_strength is not None else 0.5

        score = 0
        if rsi > 70:
            score += 1
        elif rsi < 30:
            score -= 1

        if last_price > upper_band:
            score += 1
        elif last_price < lower_band:
            score -= 1

        if book_ratio > 0.6:
            score += 1
        elif book_ratio < 0.4:
            score -= 1

        if strength > 0.6:
            score += 1
        elif strength < 0.4:
            score -= 1

        if vol_change > 0.2:
            score += 1
        elif vol_change < -0.2:
            score -= 1

        if score <= -3:
            self.state = self.LEVELS[0]
        elif score <= -1:
            self.state = self.LEVELS[1]
        elif score <= 1:
            self.state = self.LEVELS[2]
        elif score <= 3:
            self.state = self.LEVELS[3]
        else:
            self.state = self.LEVELS[4]

        return self.state
