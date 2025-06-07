import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class LearningAgent:
    """Persistently learn strategy weights from trade history."""

    def __init__(self, state_path: str | Path | None = None) -> None:
        self.state_path = Path(state_path) if state_path else Path("data/learning_state.json")
        self.weights: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []
        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.weights = data.get("weights", {})
            self.history = data.get("history", [])
        except FileNotFoundError:
            self.weights = {}
            self.history = []

    def _save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"weights": self.weights, "history": self.history}
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def record_trade(
        self,
        strategy: str,
        return_rate: float,
        market_phase: str | None = None,
        emotion_score: float | None = None,
        risk: float | None = None,
    ) -> None:
        """Store trade result with additional context."""
        self.history.append(
            {
                "strategy": strategy,
                "return": return_rate,
                "market_phase": market_phase,
                "emotion": emotion_score,
                "risk": risk,
                "timestamp": time.time(),
            }
        )
        self._save()

    def update(self, trade_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, float]:
        """Update strategy weights using the last month of trades."""

        history = trade_history if trade_history is not None else self.history
        one_month_ago = time.time() - 30 * 24 * 3600
        recent = [t for t in history if t.get("timestamp", 0) >= one_month_ago]

        grouped: Dict[str, List[Dict[str, Any]]] = {}
        for trade in recent:
            grouped.setdefault(trade.get("strategy"), []).append(trade)

        for name, trades in grouped.items():
            rets = [t.get("return", 0.0) for t in trades]
            avg_ret = sum(rets) / len(rets)
            trend = sum(1 if r > 0 else -1 for r in rets[-3:])

            phase_counts: Dict[str, int] = {}
            for t in trades:
                phase = t.get("market_phase")
                if phase:
                    phase_counts[phase] = phase_counts.get(phase, 0) + 1
            phase_ratio = 0.0
            if phase_counts:
                phase_ratio = max(phase_counts.values()) / len(trades)

            emotion = sum(t.get("emotion", 0.0) for t in trades) / len(trades)

            score = avg_ret + 0.1 * trend + 0.1 * emotion + 0.5 * phase_ratio
            old = self.weights.get(name, 1.0)
            self.weights[name] = old * 0.9 + score * 0.1

        # purge consistently poor strategies
        for name in list(self.weights.keys()):
            if self.weights[name] < -1:
                del self.weights[name]

        self._save()
        return self.weights

    def adjust_from_signal(self, strategy: str, score_percent: float, confidence: float | None) -> None:
        """Lightweight online adjustment using condition score and confidence."""
        conf = confidence if confidence is not None else 1.0
        weight = self.weights.get(strategy, 1.0)
        weight += 0.01 * (score_percent / 100.0) * conf
        self.weights[strategy] = weight
        self._save()

