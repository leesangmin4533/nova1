from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

from .data.pipeline import MarketData


@dataclass
class Position:
    entry_price: float
    size: float


@dataclass
class PositionManager:
    target_return: float = 0.15
    stop_loss: float = -0.15
    position: Optional[Position] = None

    async def run(self, stream: asyncio.Queue[MarketData]) -> Optional[str]:
        if self.position is None:
            return None
        market_data = await stream.get()
        price = market_data.price
        pnl = (price - self.position.entry_price) / self.position.entry_price
        signal = None
        if pnl >= self.target_return or pnl <= self.stop_loss:
            signal = "CLOSE"
            self.position = None
        stream.task_done()
        await asyncio.sleep(1)
        return signal
