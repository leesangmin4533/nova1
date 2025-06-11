import json
from pathlib import Path
from config import LOG_BASE_DIR


DECISION_PATH = LOG_BASE_DIR / "판단" / "latest_decision.json"
NEWS_PATH = LOG_BASE_DIR / "뉴스반영" / "latest_news.json"


def get_latest_decision() -> dict:
    """Return the latest decision data if available."""
    try:
        with open(DECISION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_latest_news() -> dict:
    """Return the latest news sentiment data if available."""
    try:
        with open(NEWS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
