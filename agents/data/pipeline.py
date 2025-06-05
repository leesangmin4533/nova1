from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class MarketData:
    """Placeholder structure for market data."""

    timestamp: float
    price: float
    volume: float
    bid_size: float
    ask_size: float
    trade_strength: float


class DataStream:
    """Simulated or realtime data stream."""

    def __init__(self, interval: float = 1.0) -> None:
        self.interval = interval
        self._running = False

    async def stream(self) -> AsyncIterator[MarketData]:
        self._running = True
        price = 100.0
        while self._running:
            # In a real implementation, fetch data from exchange or simulator.
            price += 0.1
            yield MarketData(
                timestamp=asyncio.get_event_loop().time(),
                price=price,
                volume=1.0,
                bid_size=0.5,
                ask_size=0.5,
                trade_strength=0.5,
            )
            await asyncio.sleep(self.interval)

    def stop(self) -> None:
        self._running = False
