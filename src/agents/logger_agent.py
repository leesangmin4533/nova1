import json
from pathlib import Path
from datetime import datetime

from .market_sentiment import MarketSentimentAgent


class LoggerAgent:
    """Log trading decisions to a single JSON file."""

    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "log.json"

    def log(self, sentiment, strategy, decision):
        current_price = MarketSentimentAgent.get_current_price()
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sentiment": sentiment,
            "strategy": strategy,
            "decision": decision,
            "current_price": current_price,
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write("\n")
