from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from .data.pipeline import MarketData
from .strategy import Strategy


class Signal:
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass
class EntryDecisionAgent:
    interval: float = 1.0
    last_price: Optional[float] = None

    async def run(
        self, stream: asyncio.Queue[MarketData], strategy: Strategy
    ) -> Signal:
        """Check entry conditions and return signal."""
        market_data = await stream.get()
        price = market_data.price
        if self.last_price is None:
            self.last_price = price
            return Signal.HOLD
        signal = Signal.HOLD
        if price > self.last_price and strategy.id == "trend_follow":
            signal = Signal.BUY
        elif price < self.last_price and strategy.id == "reversal":
            signal = Signal.SELL
        self.last_price = price
        stream.task_done()
        await asyncio.sleep(self.interval)
        return signal
