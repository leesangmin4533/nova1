import json
import threading
from pathlib import Path
from datetime import datetime
from .news_adjuster import news_adjuster

LOG_DIR = Path.home() / "log"
_lock = threading.Lock()


def _log_file_for_today() -> Path:
    date_str = datetime.now().strftime("%Y%m%d")
    return LOG_DIR / f"log_{date_str}.jsonl"


def save_log(entry: dict) -> None:
    """Append ``entry`` as a JSON object to today's ``.jsonl`` file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    path = _log_file_for_today()
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class LoggerAgent:
    """Log actions and agent outputs to JSON files."""

    def __init__(self, log_dir: str | Path | None = None):
        self.log_dir = Path(log_dir) if log_dir else LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.last_log = None
        self.judgment_dir = self.log_dir / "판단로그"
        self.judgment_dir.mkdir(parents=True, exist_ok=True)

    def log_event(self, data: dict) -> str:
        """Write an arbitrary event dictionary to a JSON file."""
        timestamp = datetime.utcnow().isoformat()
        data = dict(data)
        data.setdefault("timestamp", timestamp)
        save_log(data)
        return data["timestamp"]

    def log_success(
        self,
        agent: str,
        action: str,
        *,
        price: float,
        strategy: str,
        return_rate: float,
    ) -> None:
        """Record a successful trade action."""

        self.log_event(
            {
                "agent": agent,
                "action": action,
                "price": price,
                "strategy": strategy,
                "return_rate": round(return_rate, 4),
            }
        )

    def log(
        self,
        agent,
        action,
        price=None,
        confidence=None,
        symbol=None,
        return_rate=None,
        *,
        reason: str | None = None,
    ):
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp,
            "agent": agent,
            "action": action,
            "price": price,
            "confidence": confidence,
            "symbol": symbol,
            "return_rate": return_rate,
        }

        if action in {"BUY", "SELL"}:
            entry.setdefault(
                "reason",
                reason
                or "뉴스 기반 전략 반영: 시장 심리 기대(0.36) → RSI –3, 민감도 +0.5 외",
            )
            entry.setdefault("source", str(news_adjuster.news_path))
            news_adjuster.schedule_feedback(action, price or 0.0, symbol or "")

        compare = {
            "agent": agent,
            "action": action,
            "price": price,
            "symbol": symbol,
            "return_rate": return_rate,
        }
        if self.last_log and all(compare.get(k) == self.last_log.get(k) for k in compare):
            return None

        self.last_log = compare

        save_log(entry)
        return timestamp

    def get_recent_trades(self, limit: int = 10):
        """Return recent BUY/SELL/CLOSE log entries."""
        from log_analyzer import load_logs

        logs = load_logs(str(LOG_DIR))
        trades = [
            l
            for l in logs
            if l.get("action") in {"BUY", "SELL", "CLOSE"}
        ]
        return trades[-limit:]

    # ------------------------------------------------------------------
    def _judgment_file_for_today(self) -> Path:
        date_str = datetime.now().strftime("%Y%m%d")
        return self.judgment_dir / f"{date_str}_log.json"

    def log_judgment(
        self,
        *,
        action: str,
        reason: str | None,
        indicators: dict,
        market_emotion: str,
        human_likely_action: str,
        score_vs_human: int,
        strategy_version: str,
        result_after_5min: float | None = None,
        result_after_30min: float | None = None,
        conflict_analysis: dict | None = None,
    ) -> None:
        entry = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "reason": reason,
            "indicators": indicators,
            "market_emotion": market_emotion,
            "human_likely_action": human_likely_action,
            "score_vs_human": score_vs_human,
            "strategy_version": strategy_version,
            "result_after_5min": result_after_5min,
            "result_after_30min": result_after_30min,
            "conflict_analysis": conflict_analysis,
        }

        path = self._judgment_file_for_today()
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

