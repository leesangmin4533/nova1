from statistics import mean
from typing import List, Dict, Any, Tuple
from .market_sentiment import MarketSentimentAgent


class EntryDecisionAgent:
    """Determine trade entry signals."""

    def __init__(self, broker):
        self.broker = broker

    def _ma(self, prices: List[float], period: int) -> float:
        return mean(prices[:period]) if len(prices) >= period else mean(prices)

    def evaluate(
        self,
        strategy: Tuple[str, Dict[str, Any]],
        chart_data: List[Dict[str, Any]],
        order_status: Dict[str, Any],
    ) -> str:
        """Return BUY, SELL, or HOLD signal based on MA cross and RSI."""
        closes = [c["trade_price"] for c in chart_data]
        if len(closes) < 20:
            return "HOLD"
        short_ma = self._ma(closes, 5)
        long_ma = self._ma(closes, 20)
        rsi = MarketSentimentAgent._rsi(closes)

        if short_ma > long_ma and rsi > 55:
            # send buy order via broker
            try:
                self.broker.place_order("buy")
            except Exception:
                pass
            return "BUY"
        if short_ma < long_ma and rsi < 45:
            try:
                self.broker.place_order("sell")
            except Exception:
                pass
            return "SELL"
        return "HOLD"
