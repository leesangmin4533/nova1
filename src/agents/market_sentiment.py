from statistics import mean, stdev
from typing import List, Dict, Any


class MarketSentimentAgent:
    """Agent that classifies market sentiment into five levels."""

    LEVELS = ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]

    def __init__(self):
        self.state = "NEUTRAL"

    @staticmethod
    def _rsi(prices: List[float], period: int = 14) -> float:
        if len(prices) < period + 1:
            return 50.0
        gains, losses = [], []
        for i in range(1, len(prices)):
            delta = prices[i] - prices[i - 1]
            gains.append(max(delta, 0))
            losses.append(max(-delta, 0))
        avg_gain = mean(gains[-period:])
        avg_loss = mean(losses[-period:])
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def update(self, candle_data: List[Dict[str, Any]], order_book: Dict[str, Any], trade_strength: float) -> str:
        """Update sentiment based on market data."""
        closes = [c["trade_price"] for c in candle_data]
        rsi = self._rsi(closes)
        volume_change = 0.0
        if len(candle_data) >= 2:
            vol_now = candle_data[0].get("candle_acc_trade_volume", 0)
            vol_prev = candle_data[1].get("candle_acc_trade_volume", vol_now)
            volume_change = (vol_now - vol_prev) / max(vol_prev, 1)
        bid = order_book.get("total_bid_size", 0)
        ask = order_book.get("total_ask_size", 0)
        bid_ask_ratio = bid / ask if ask else 1

        sma = mean(closes[:20]) if len(closes) >= 20 else mean(closes)
        std = stdev(closes[:20]) if len(closes) >= 20 else stdev(closes)
        upper_band = sma + 2 * std
        lower_band = sma - 2 * std
        price = closes[0]

        if rsi < 25 and price < lower_band and bid_ask_ratio < 0.8:
            self.state = self.LEVELS[0]
        elif rsi < 45:
            self.state = self.LEVELS[1]
        elif rsi > 75 and price > upper_band and bid_ask_ratio > 1.2:
            self.state = self.LEVELS[4]
        elif rsi > 60:
            self.state = self.LEVELS[3]
        else:
            self.state = self.LEVELS[2]
        return self.state
