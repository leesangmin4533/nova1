"""Evaluate entry signals based on current strategy."""

from __future__ import annotations

from typing import Iterable, Mapping, Tuple


class EntryDecisionAgent:
    """Determine trade entry signals."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def _rsi(prices: Iterable[float], period: int = 14) -> float:
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

    def evaluate(
        self,
        strategy: Tuple[str, Mapping],
        chart_data: Iterable[Mapping[str, float]] | None,
        order_status: Mapping | None,
    ) -> str:
        """Return BUY, SELL, or HOLD signal."""

        name, params = strategy
        prices = [c.get("close", 0.0) for c in chart_data or []]

        if name == "trend_follow" and len(prices) >= 20:
            short = sum(prices[-5:]) / 5
            long = sum(prices[-20:]) / 20
            rsi = self._rsi(prices)
            if short > long and rsi > 55:
                return "BUY"
            if short < long and rsi < 45:
                return "SELL"

        if name == "reversal" and len(prices) >= params.get("lookback", 20):
            lookback = params.get("lookback", 20)
            recent = prices[-lookback:]
            if prices[-1] > max(recent):
                return "SELL"
            if prices[-1] < min(recent):
                return "BUY"

        # other strategies can be added here

        return "HOLD"
