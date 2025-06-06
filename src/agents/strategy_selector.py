class StrategySelector:
    """Select trading strategy based on market sentiment and learned weights."""

    def __init__(self):
        self.current_strategy = None
        self.strategy_mode = "HOLD"
        self.market_phase = "NEUTRAL"
        self.strategy_scores = {
            "reversal": 1.0,
            "swing": 1.0,
            "trend_follow": 1.0,
            "momentum": 1.0,
            "take_profit": 1.0,
        }

    def update_market_phase(self, rsi, bb_score):
        """Update internal market phase state from RSI and BB score."""

        if rsi < 30:
            self.market_phase = "FEAR"
        elif rsi > 85:
            self.market_phase = "GREED"
        else:
            self.market_phase = "NEUTRAL"

    def update_scores(self, weights):
        """Update internal strategy scores from learning agent."""
        if not weights:
            return
        for name, score in weights.items():
            self.strategy_scores[name] = score

    def select(self, sentiment):
        """Select a strategy ID using softmax of weights and market state."""
        import math
        import random

        if isinstance(sentiment, dict):
            self.update_market_phase(sentiment.get("rsi", 50), sentiment.get("bb_score", 0))
            sentiment_level = sentiment.get("level", "NEUTRAL")
        else:
            sentiment_level = sentiment

        mapping = {
            "EXTREME_FEAR": [],
            "FEAR": ["swing"],
            "NEUTRAL": ["trend_follow", "momentum"],
            "GREED": ["trend_follow", "reversal"],
            "EXTREME_GREED": ["reversal", "take_profit"],
        }
        candidates = mapping.get(sentiment_level, list(self.strategy_scores.keys()))
        candidate_scores = {k: self.strategy_scores.get(k, 1.0) for k in candidates}
        if not candidate_scores:
            self.strategy_mode = "HOLD"
            return "hold", {"weight": 1.0}, 0.0

        preferred = None
        if self.market_phase == "FEAR":
            preferred = "reversal"
        elif self.market_phase == "GREED":
            preferred = "reversal"
        else:
            preferred = "momentum"

        if preferred in candidate_scores:
            candidate_scores = {preferred: candidate_scores[preferred]}

        tau = 0.2
        exp_scores = {k: math.exp(v / tau) for k, v in candidate_scores.items()}
        total = sum(exp_scores.values())
        probs = {k: exp_scores[k] / total for k in exp_scores}
        strategies = list(probs.keys())
        weights = list(probs.values())
        choice = random.choices(strategies, weights=weights, k=1)[0]
        mode_map = {
            "trend_follow": "TREND",
            "momentum": "TREND",
            "swing": "BOX",
            "reversal": "REVERSAL",
            "take_profit": "REVERSAL",
        }
        self.strategy_mode = mode_map.get(choice, "HOLD")
        weight = self.strategy_scores.get(choice, 1.0)
        params = {"weight": weight}
        self.current_strategy = (choice, params)
        return choice, params, probs[choice]
