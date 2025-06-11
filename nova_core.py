import json
from pathlib import Path
from datetime import datetime
from config import LOG_BASE_DIR, DECISION_PATH

NEWS_PATH = LOG_BASE_DIR / "뉴스반영" / "latest_news.json"


def get_latest_decision() -> dict:
    """Return the latest decision data if available."""
    try:
        with open(DECISION_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_decision(action: str, reason: str, human_action: str, score_vs_human, **extra) -> None:
    """Write a decision entry to ``DECISION_PATH``.

    Additional keyword arguments are merged into the saved JSON data.
    """
    decision = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "action": action,
        "reason": reason,
        "human_likely_action": human_action,
        "score_vs_human": score_vs_human,
    }
    decision.update(extra)
    Path(DECISION_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(DECISION_PATH, "w", encoding="utf-8") as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)


def get_latest_news() -> dict:
    """Return the latest news sentiment data if available."""
    try:
        with open(NEWS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
