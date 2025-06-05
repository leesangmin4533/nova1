class PositionManager:
    """Manage open positions."""

    def __init__(self):
        self.positions = []

    def update(self, position, entry_price, current_price):
        """Return CLOSE if exit conditions are met."""
        if position is None:
            return None
        pnl = (current_price - entry_price) / entry_price
        if pnl >= 0.15 or pnl <= -0.15:
            return "CLOSE"
        return None
