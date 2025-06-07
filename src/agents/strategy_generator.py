import json
import random
from pathlib import Path
from typing import Any, Dict, List, Optional


class StrategyGenerator:
    """Generate and evolve simple trading strategy definitions."""

    def __init__(self, *, seed: Optional[int] = None) -> None:
        self.rng = random.Random(seed)
        self.generated: List[Dict[str, Any]] = []

    # condition builders -------------------------------------------------
    def _ma_condition(self) -> Dict[str, Any]:
        period = self.rng.choice([5, 10, 20, 30, 60])
        direction = self.rng.choice([">", "<"])
        return {"type": "MA", "period": period, "direction": direction}

    def _rsi_condition(self) -> Dict[str, Any]:
        period = self.rng.choice([14, 20])
        level = self.rng.choice([30, 45, 55, 70])
        op = self.rng.choice([">", "<"])
        return {"type": "RSI", "period": period, "level": level, "op": op}

    def _macd_condition(self) -> Dict[str, Any]:
        fast = self.rng.choice([12, 26])
        slow = self.rng.choice([26, 52])
        signal = self.rng.choice([9, 12])
        return {"type": "MACD", "fast": fast, "slow": slow, "signal": signal}

    # generation ---------------------------------------------------------
    def create_strategy(self) -> Dict[str, Any]:
        """Return a randomly generated strategy dictionary."""
        conds = []
        for _ in range(self.rng.randint(1, 3)):
            builder = self.rng.choice(
                [self._ma_condition, self._rsi_condition, self._macd_condition]
            )
            conds.append(builder())
        strat = {"id": f"gen_{len(self.generated)}", "conditions": conds}
        self.generated.append(strat)
        return strat

    # evolutionary operations -------------------------------------------
    def mutate(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        new = json.loads(json.dumps(strategy))
        if new.get("conditions"):
            idx = self.rng.randrange(len(new["conditions"]))
            cond = new["conditions"][idx]
            if cond["type"] == "MA":
                cond["period"] = max(2, cond["period"] + self.rng.choice([-5, 5]))
            elif cond["type"] == "RSI":
                cond["level"] = min(100, max(0, cond["level"] + self.rng.choice([-5, 5])))
            elif cond["type"] == "MACD":
                cond["signal"] = max(1, cond["signal"] + self.rng.choice([-1, 1]))
        new["id"] = f"gen_{len(self.generated)}"
        self.generated.append(new)
        return new

    def crossover(self, a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new strategy by combining two parents."""
        ac = a.get("conditions", [])
        bc = b.get("conditions", [])
        pivot_a = self.rng.randint(0, len(ac)) if ac else 0
        pivot_b = self.rng.randint(0, len(bc)) if bc else 0
        conds = ac[:pivot_a] + bc[pivot_b:]
        if not conds:
            return self.mutate(a if self.rng.random() < 0.5 else b)
        strat = {"id": f"gen_{len(self.generated)}", "conditions": conds}
        self.generated.append(strat)
        return strat

    def evolve(
        self,
        strategies: List[Dict[str, Any]],
        performance: List[float],
        *,
        mutation_rate: float = 0.2,
    ) -> List[Dict[str, Any]]:
        """Return evolved strategies using simple selection logic."""
        if not strategies:
            return []
        paired = list(zip(strategies, performance))
        paired.sort(key=lambda x: x[1], reverse=True)
        parents = [s for s, _ in paired[: max(1, len(paired) // 2)]]
        children = []
        for _ in range(len(strategies)):
            if self.rng.random() < mutation_rate:
                base = self.rng.choice(parents)
                children.append(self.mutate(base))
            else:
                a, b = self.rng.sample(parents, k=2) if len(parents) >= 2 else (parents[0], parents[0])
                children.append(self.crossover(a, b))
        return children

    # persistence --------------------------------------------------------
    def save(self, path: str | Path) -> None:
        data = {"strategies": self.generated}
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, path: str | Path) -> List[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.generated = data.get("strategies", [])
        except FileNotFoundError:
            self.generated = []
        return self.generated
