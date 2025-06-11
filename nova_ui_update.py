"""Background updater for the legacy NOVA HTML UI."""

from __future__ import annotations

import json
import threading
import time
import webbrowser
from pathlib import Path

from upbit_api import get_orderbook, get_current_price
from nova_core import get_latest_decision, get_latest_news
from config import LOG_BASE_DIR, UI_PATH


UI_DATA_PATH = LOG_BASE_DIR / "UI" / "ui_data.json"


def update_ui(symbol: str = "KRW-BTC") -> None:
    prev_hash: str | None = None
    while True:
        try:
            orderbook = get_orderbook(symbol)
            price_info = get_current_price(symbol)
            decision = get_latest_decision()
            news = get_latest_news()

            ui_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "price": price_info.get("trade_price"),
                "change_rate": price_info.get("signed_change_rate"),
                "orderbook": orderbook,
                "action": decision.get("action"),
                "reason": decision.get("reason"),
                "source_news": decision.get("source_news", []),
                "score_vs_human": decision.get("score_vs_human"),
                "news": news,
            }

            UI_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(UI_DATA_PATH, "w", encoding="utf-8") as f:
                json.dump(ui_data, f, ensure_ascii=False, indent=2)
        except Exception as exc:  # pragma: no cover - runtime errors only
            print("UI update error:", exc)

        time.sleep(2)


def launch_ui() -> None:
    if Path(UI_PATH).exists():
        webbrowser.open(Path(UI_PATH).as_uri())
    else:
        print("UI HTML 파일이 존재하지 않습니다.")


if __name__ == "__main__":
    threading.Thread(target=update_ui, daemon=True).start()
    launch_ui()
