import aiohttp
import hmac
import hashlib
import time
import uuid
import os
from typing import Dict, Any, List


class UpbitBroker:
    """Simplified broker for placing orders on Upbit."""

    BASE_URL = "https://api.upbit.com/v1"

    def __init__(self, access_key: str = None, secret_key: str = None):
        self.access_key = access_key or os.getenv("UPBIT_ACCESS_KEY", "")
        self.secret_key = secret_key or os.getenv("UPBIT_SECRET_KEY", "")

    async def _auth_headers(self, query: str = "") -> Dict[str, str]:
        nonce = str(uuid.uuid4())
        m = hashlib.sha512()
        m.update(query.encode("utf-8"))
        q_hash = m.hexdigest()
        payload = f"access_key={self.access_key}&nonce={nonce}&query_hash={q_hash}&query_hash_alg=SHA512"
        jwt_token = hmac.new(self.secret_key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha512).hexdigest()
        return {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}

    async def place_order(self, side: str, volume: str, price: str, market: str = "KRW-BTC") -> Any:
        query = f"market={market}&side={side}&volume={volume}&price={price}&ord_type=limit"
        headers = await self._auth_headers(query)
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.BASE_URL}/orders?{query}", headers=headers) as resp:
                if resp.status != 201:
                    raise Exception(f"Order failed: {resp.status}")
                return await resp.json()


class PaperBroker:
    """Simulated broker that records orders without executing them."""

    def __init__(self):
        self.orders: List[Dict[str, Any]] = []

    def place_order(self, side: str, volume: str = "0", price: str = "0", market: str = "KRW-BTC") -> Dict[str, Any]:
        """Record an order and return confirmation."""
        order = {"side": side, "volume": volume, "price": price, "market": market, "timestamp": time.time()}
        self.orders.append(order)
        return order

