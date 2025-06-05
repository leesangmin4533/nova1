import aiohttp
import asyncio
from typing import Any, Dict


class UpbitClient:
    BASE_URL = "https://api.upbit.com/v1"

    async def _get(self, session: aiohttp.ClientSession, path: str, params=None) -> Any:
        url = f"{self.BASE_URL}/{path}"
        async with session.get(url, params=params, timeout=10) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def fetch_candle(self, market: str = "KRW-BTC", unit: int = 1) -> Dict[str, Any]:
        params = {"market": market, "count": 50}
        path = f"candles/minutes/{unit}"
        async with aiohttp.ClientSession() as session:
            data = await self._get(session, path, params)
            return data

    async def fetch_orderbook(self, market: str = "KRW-BTC") -> Dict[str, Any]:
        params = {"markets": market}
        async with aiohttp.ClientSession() as session:
            data = await self._get(session, "orderbook", params)
            return data[0] if data else {}

    async def fetch_trades(self, market: str = "KRW-BTC") -> Dict[str, Any]:
        params = {"market": market, "count": 50}
        async with aiohttp.ClientSession() as session:
            data = await self._get(session, "trades/ticks", params)
            return data

