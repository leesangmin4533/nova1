"""Simple WebSocket price feed for Upbit."""

from __future__ import annotations

import json
import threading

try:
    import websocket  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    class _DummyWebSocketApp:
        def __init__(self, *_, **__):
            raise RuntimeError("websocket-client library not available")

    class _DummyModule:
        WebSocketApp = _DummyWebSocketApp

    websocket = _DummyModule()


class UpbitWebSocket:
    """Subscribe to real-time trade price via Upbit WebSocket."""

    def __init__(self, ticker: str = "KRW-BTC") -> None:
        self.ticker = ticker
        self.latest_price: float | None = None
        self.ws: websocket.WebSocketApp | None = None

    # ------------------------------------------------------------------
    def on_message(self, ws: websocket.WebSocketApp, message: str) -> None:
        data = json.loads(message)
        self.latest_price = data.get("trade_price")
        print(f"[실시간 시세] {self.ticker}: {self.latest_price}")

    def on_error(self, ws: websocket.WebSocketApp, error: Exception) -> None:
        print(f"[WebSocket 오류] {error}")

    def on_close(
        self,
        ws: websocket.WebSocketApp,
        close_status_code: int | None,
        close_msg: str | None,
    ) -> None:
        print("[WebSocket 종료됨]")

    def on_open(self, ws: websocket.WebSocketApp) -> None:
        payload = [{"ticket": "price_feed"}, {"type": "trade", "codes": [self.ticker]}]
        ws.send(json.dumps(payload))

    # ------------------------------------------------------------------
    def run(self) -> None:
        """Start the WebSocket connection in a background thread."""
        self.ws = websocket.WebSocketApp(
            "wss://api.upbit.com/websocket/v1",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open,
        )
        thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        thread.start()

    def get_latest_price(self) -> float | None:
        """Return the most recent trade price received."""
        return self.latest_price
