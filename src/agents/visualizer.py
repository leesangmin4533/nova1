class VisualizerAgent:
    """Store the latest state for the web dashboard."""

    def __init__(self):
        self.state = {
            "sentiment": "NEUTRAL",
            "strategy": None,
            "position": None,
            "signal": "HOLD",
            "price": None,
            "balance": 0.0,
            "equity": 0.0,
        }

    def update_state(self, sentiment, strategy, position, signal, price, balance):
        equity = balance
        if position and isinstance(position, dict):
            qty = position.get("quantity", 1.0)
            equity += price * qty
        self.state.update(
            {
                "sentiment": sentiment,
                "strategy": strategy,
                "position": position,
                "signal": signal,
                "price": price,
                "balance": balance,
                "equity": equity,
            }
        )
