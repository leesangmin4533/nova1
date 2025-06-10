import sys
import subprocess
import time
import webbrowser

try:
    from pyngrok import ngrok
except ImportError:  # pragma: no cover - auto install for convenience
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyngrok"])
    from pyngrok import ngrok

from status_server import start_status_server, update_state
from main import TradingApp, SYMBOL
from config import USE_NGROK, NGROK_PORT, LOCAL_SERVER_PORT
from agents.utils import get_upbit_orderbook


def main():
    app = TradingApp()
    start_status_server(
        port=LOCAL_SERVER_PORT,
        position_manager=app.position_manager,
        logger_agent=app.logger,
    )

    url = f"http://localhost:{LOCAL_SERVER_PORT}"
    if USE_NGROK:
        public_url = ngrok.connect(NGROK_PORT)
        print(f"\N{link symbol} 외부 접속 주소: {public_url}")
        url = str(public_url)

    try:
        webbrowser.open(url)
    except Exception:
        pass

    symbol = SYMBOL
    while True:
        orderbook = get_upbit_orderbook(symbol)
        update_state(
            bids=[[b["price"], b["volume"]] for b in orderbook.get("bids", []) if b.get("volume")],
            asks=[[a["price"], a["volume"]] for a in orderbook.get("asks", []) if a.get("volume")],
            bid_volume=orderbook.get("bid_volume"),
            ask_volume=orderbook.get("ask_volume"),
            buy_count=app.position_manager.total_buys,
            sell_count=app.position_manager.total_sells,
        )
        app.loop()
        time.sleep(2)


if __name__ == "__main__":
    main()
