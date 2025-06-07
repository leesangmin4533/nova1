import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Callable


ANALYSIS_DELAY_SEC = 5 * 60  # 5 minutes
THRESHOLD_PCT = 1.0
MIN_CONFIDENCE = 50.0

LOG_DIR = Path.home() / "log" / "missed_hold"
LOG_FILE = LOG_DIR / "failed_holds.jsonl"


def _default_price_fetcher(symbol: str) -> float:
    """Fetch the latest closing price for the given symbol."""
    from .utils import get_upbit_candles

    return get_upbit_candles(symbol, 1)[-1]


async def _check_after_delay(
    decision_info: dict,
    price_at_decision: float,
    symbol: str,
    fetcher: Callable[[str], float],
) -> None:
    await asyncio.sleep(ANALYSIS_DELAY_SEC)
    try:
        price_after = fetcher(symbol)
    except Exception:
        return

    change_pct = (price_after - price_at_decision) / price_at_decision * 100
    if (
        change_pct > THRESHOLD_PCT
        and decision_info.get("confidence", 0.0) >= MIN_CONFIDENCE
    ):
        entry = {
            "symbol": symbol,
            "timestamp": decision_info.get("timestamp", datetime.now().isoformat()),
            "confidence": decision_info.get("confidence"),
            "price_at_decision": price_at_decision,
            "price_after_5min": price_after,
            "price_change_pct": round(change_pct, 2),
            "verdict": "MISSED_BUY_OPPORTUNITY",
        }
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def track_failed_hold(
    decision_info: dict,
    current_price: float,
    symbol: str,
    *,
    price_fetcher: Callable[[str], float] | None = None,
) -> None:
    """Schedule a check to log missed opportunities after a HOLD decision."""
    if decision_info.get("action") != "HOLD":
        return

    fetcher = price_fetcher or _default_price_fetcher

    async def runner() -> None:
        await _check_after_delay(decision_info, current_price, symbol, fetcher)

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(runner())
    else:
        asyncio.get_event_loop().run_in_executor(None, asyncio.run, runner())

