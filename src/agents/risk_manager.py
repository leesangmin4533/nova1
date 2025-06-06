class RiskManager:
    """Adjust order amounts based on volatility and manage exposure."""

    def __init__(self, max_trade_pct: float = 0.1) -> None:
        self.max_trade_pct = max_trade_pct

    def order_amount(self, balance: float, volatility: float) -> float:
        """Return recommended order amount."""
        factor = max(0.5, 1 - volatility * 50)
        return balance * self.max_trade_pct * factor
