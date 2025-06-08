import json
from datetime import datetime
from pathlib import Path
from config import LOG_BASE_DIR
from typing import Dict, Iterable

DEFAULT_WEIGHTS: Dict[str, float] = {
    "rsi_above_55": 0.25,
    "ma_cross": 0.2,
    "golden_cross": 0.25,
    "orderbook_bias_up": 0.15,
    "volatility_threshold": 0.15,
}


class StrategyScorer:
    """Compute weighted condition scores and tune weights from failures."""

    def __init__(
        self,
        weights: Dict[str, float] | None = None,
        *,
        log_dir: str | Path | None = None,
        history_file: str = "weight_changes.jsonl",
    ) -> None:
        self.weights: Dict[str, float] = dict(DEFAULT_WEIGHTS)
        if weights:
            self.weights.update(weights)
        base = Path(log_dir) if log_dir is not None else LOG_BASE_DIR / "strategy_scorer"
        base.mkdir(parents=True, exist_ok=True)
        self.log_dir = base
        self.history_path = base / history_file

    def score(self, conditions: Dict[str, bool]) -> float:
        """Return overall score percentage from condition pass map."""
        total = 0.0
        for name, passed in conditions.items():
            if passed:
                total += self.weights.get(name, 0.0)
        return total * 100

    def tune_weights(self, failed: Iterable[str], alpha: float = 0.1) -> None:
        """Soft-update weights based on failed condition names."""
        updates: Dict[str, Dict[str, float]] = {}
        for cond in failed:
            if cond not in self.weights:
                continue
            old = self.weights[cond]
            new = max(0.0, old * (1 - alpha))
            if new != old:
                self.weights[cond] = new
                updates[cond] = {"old": old, "new": new}
        if updates:
            self._record_updates(updates)

    def _record_updates(self, updates: Dict[str, Dict[str, float]]) -> None:
        entry = {"timestamp": datetime.utcnow().isoformat(), "updates": updates}
        with open(self.history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
