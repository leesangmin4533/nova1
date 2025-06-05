# Utility functions for NOVA strategy handling

from typing import Dict, List, Any


def generate_nova_strategy_json(
    name: str,
    condition: str,
    inputs: List[str],
    version: str = "v1.0",
    use_score: bool = True,
    threshold: float = 0.65,
    on_fail: str = "log_and_decay_weight",
    active_time: str = "09:00-10:30",
    meta: str = "",
) -> Dict[str, Any]:
    """Return a standardized strategy description dictionary."""
    return {
        "strategy": name,
        "condition": condition,
        "inputs": inputs,
        "version": version,
        "use_score": use_score,
        "score_threshold": threshold,
        "on_fail": on_fail,
        "active_time": active_time,
        "meta": meta,
    }


def adjust_weights(
    weights: Dict[str, float],
    stats: Dict[str, Dict[str, int]],
    decay_rate: float = 0.2,
    threshold: float = 0.7,
) -> Dict[str, float]:
    """Decrease weights for frequently failing conditions."""
    for cond, stat in stats.items():
        total = max(stat.get("total", 0), 1)
        fail_rate = stat.get("failures", 0) / total
        if fail_rate >= threshold:
            weights[cond] = max(0.0, weights.get(cond, 0.0) - decay_rate)
    return weights
