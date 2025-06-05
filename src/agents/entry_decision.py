"""Trade entry decision agent."""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np


class EntryDecisionAgent:
    """Determine trade entry signals."""

    def __init__(self) -> None:
        pass

    def _rsi(self, closes: List[float], period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        deltas = np.diff(closes[-(period + 1) :])
        gains = np.clip(deltas, 0, None).sum()
        losses = np.abs(np.clip(deltas, None, 0)).sum()
        if losses == 0:
            return 100.0
        rs = gains / losses
        return 100 - 100 / (1 + rs)

    def evaluate(
        self, strategy: Tuple[str, Dict], chart_data: Dict[str, List[float]], order_status
    ) -> str:
        """Return BUY, SELL, or HOLD signal."""
        closes = chart_data.get("close", [])
        if len(closes) < 20:
            return "HOLD"

        sma_short = float(np.mean(closes[-5:]))
        sma_long = float(np.mean(closes[-20:]))
        rsi_val = self._rsi(closes)

        if sma_short > sma_long and rsi_val > 55:
            return "BUY"
        if sma_short < sma_long and rsi_val < 45:
            return "SELL"
        return "HOLD"
