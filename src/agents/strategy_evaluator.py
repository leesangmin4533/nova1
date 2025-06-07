import statistics
from typing import Any, Dict, Iterable, List, Tuple


class StrategyEvaluator:
    """Compute performance metrics for generated strategies."""

    def __init__(self) -> None:
        pass

    # ------------------------------------------------------------------
    @staticmethod
    def _max_drawdown(returns: Iterable[float]) -> float:
        cum = 0.0
        peak = 0.0
        max_dd = 0.0
        for r in returns:
            cum += r
            peak = max(peak, cum)
            dd = peak - cum
            max_dd = max(max_dd, dd)
        return max_dd

    def _sqn(self, returns: List[float]) -> float:
        if len(returns) < 2:
            return 0.0
        avg = statistics.mean(returns)
        std = statistics.stdev(returns)
        if std == 0:
            return 0.0
        return (avg / std) * (len(returns) ** 0.5)

    # ------------------------------------------------------------------
    def market_fit(self, trades: Iterable[Dict[str, Any]]) -> Tuple[str, float]:
        counts: Dict[str, int] = {}
        total = 0
        for t in trades:
            phase = t.get("market_phase")
            if not phase:
                continue
            counts[phase] = counts.get(phase, 0) + 1
            total += 1
        if not counts or total == 0:
            return "UNKNOWN", 0.0
        best = max(counts, key=counts.get)
        ratio = counts[best] / total
        return best, ratio

    def mfe_mae(self, trades: Iterable[Dict[str, Any]]) -> Tuple[float, float]:
        mfes: List[float] = []
        maes: List[float] = []
        for t in trades:
            mfes.append(t.get("max_profit", 0.0))
            maes.append(t.get("max_loss", 0.0))
        avg_mfe = statistics.mean(mfes) if mfes else 0.0
        avg_mae = statistics.mean(maes) if maes else 0.0
        return avg_mfe, avg_mae

    def evaluate(self, returns: List[float], trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Return evaluation metrics for a strategy."""
        total_return = sum(returns)
        max_dd = self._max_drawdown(returns)
        sqn = self._sqn(returns)
        phase, fit_ratio = self.market_fit(trades)
        avg_mfe, avg_mae = self.mfe_mae(trades)
        return {
            "total_return": total_return,
            "max_drawdown": max_dd,
            "sqn": sqn,
            "market_fit": phase,
            "fit_ratio": fit_ratio,
            "avg_mfe": avg_mfe,
            "avg_mae": avg_mae,
        }
