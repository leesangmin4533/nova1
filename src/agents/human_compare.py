from typing import Literal


class HumanCompareAgent:
    """Predict human trader action based on simple RSI thresholds."""

    def predict(self, rsi: float) -> Literal["BUY", "SELL", "HOLD"]:
        if rsi < 30:
            return "BUY"
        if rsi > 70:
            return "SELL"
        return "HOLD"

    def score_vs_human(self, agent_action: str, human_action: str) -> int:
        """Return comparison score as +1, 0, or -1."""
        if agent_action == human_action:
            return 0
        # Simplistic: assume disagreement favors human trader
        return -1
