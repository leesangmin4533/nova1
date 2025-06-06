class PositionManager:
    """Manage open positions."""

    def __init__(self):
        self.positions = []

    def update(self, position, entry_price, current_price):
        """Return CLOSE if exit conditions are met."""
        if position is None:
            return None

        if current_price >= entry_price * 1.15:
            return "CLOSE"

        if current_price <= entry_price * 0.85:
            return "CLOSE"

        return None
