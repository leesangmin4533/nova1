class StrategySelector:
    """Select trading strategy based on market sentiment and learned weights."""

    def __init__(self):
        self.current_strategy = None
        self.strategy_scores = {
            "reversal": 1.0,
            "swing": 1.0,
            "trend_follow": 1.0,
            "momentum": 1.0,
            "take_profit": 1.0,
        }

    def update_scores(self, weights):
        """Update internal strategy scores from learning agent."""
        if not weights:
            return
        for name, score in weights.items():
            self.strategy_scores[name] = score

    def select(self, sentiment):
        """Select a strategy ID using softmax of weights."""
        import math
        import random

        mapping = {
            "EXTREME_FEAR": ["reversal", "swing"],
            "FEAR": ["swing", "trend_follow"],
            "NEUTRAL": ["trend_follow", "momentum"],
            "GREED": ["momentum", "take_profit"],
            "EXTREME_GREED": ["take_profit", "momentum"],
        }
        candidates = mapping.get(sentiment, list(self.strategy_scores.keys()))
        candidate_scores = {k: self.strategy_scores.get(k, 1.0) for k in candidates}
        if not candidate_scores:
            return "hold", {"weight": 1.0}, 0.0

        tau = 0.2
        exp_scores = {k: math.exp(v / tau) for k, v in candidate_scores.items()}
        total = sum(exp_scores.values())
        probs = {k: exp_scores[k] / total for k in exp_scores}
        strategies = list(probs.keys())
        weights = list(probs.values())
        choice = random.choices(strategies, weights=weights, k=1)[0]
        weight = self.strategy_scores.get(choice, 1.0)
        params = {"weight": weight}
        self.current_strategy = (choice, params)
        return choice, params, probs[choice]
