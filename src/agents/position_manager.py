class PositionManager:
    """Manage open positions."""

    def __init__(self, take_profit: float = 0.15, stop_loss: float = -0.1, trailing: float = 0.05):
        self.positions = []
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self.trailing = trailing
        self.max_price = {}

    def update(self, position: str, entry_price: float, current_price: float):
        """Return CLOSE if exit conditions are met."""
        if position is None:
            return None
        self.max_price[position] = max(current_price, self.max_price.get(position, current_price))
        change = (current_price - entry_price) / entry_price
        if change >= self.take_profit:
            return "CLOSE"
        if change <= self.stop_loss:
            return "CLOSE"
        trail_price = self.max_price[position] * (1 - self.trailing)
        if current_price < trail_price:
            return "CLOSE"
        return None
