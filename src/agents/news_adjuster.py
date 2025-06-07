import json
from pathlib import Path
from threading import Timer
from datetime import datetime

from .utils import get_upbit_candles


class NewsAdjuster:
    """Apply strategy tweaks based on external news analysis."""

    def __init__(self, news_path=None, feedback_path=None):
        self.news_path = Path(news_path or r"C:\\Users\\kanur\\log\\뉴스반영\\2025-06-07_1135_news.json")
        self.feedback_path = Path(feedback_path or r"C:\\Users\\kanur\\log\\피드백\\2025-06-07_1135_result.json")
        self.adjustments = {
            "rsi_offset": 0,
            "decision_sensitivity": 0.0,
            "sell_trigger_sensitivity": 0.0,
            "eth_priority": 0,
            "btc_weight_offset": 0.0,
            "global_sensitivity": 0.0,
        }
        self.active = False

    def activate(self) -> None:
        """Load adjustments and enable them."""
        self._load()
        self.active = True

    # --------------------------------------------------------------
    def _load(self) -> None:
        try:
            with open(self.news_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.adjustments.update(data.get("adjustments", {}))
        except Exception:
            # Fallback to built-in defaults from instructions
            self.adjustments.update(
                {
                    "rsi_offset": -3,
                    "decision_sensitivity": 0.5,
                    "sell_trigger_sensitivity": 1.0,
                    "eth_priority": 1,
                    "btc_weight_offset": 0.02,
                    "global_sensitivity": 0.3,
                }
            )

    # --------------------------------------------------------------
    def schedule_feedback(self, action: str, price: float, symbol: str) -> None:
        """Record comparison with market price after six hours."""

        if not self.active:
            return

        def _record() -> None:
            try:
                candles = get_upbit_candles(symbol, 1)
                end_price = candles[-1]
                movement = (end_price - price) / price
                score = 1 if (movement > 0 and action == "BUY") or (
                    movement < 0 and action == "SELL"
                ) else 0
                result = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": action,
                    "price": price,
                    "end_price": end_price,
                    "score_vs_market": score,
                }
                self.feedback_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.feedback_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        Timer(6 * 3600, _record).start()


news_adjuster = NewsAdjuster()
