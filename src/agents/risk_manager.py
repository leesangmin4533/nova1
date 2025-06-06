class RiskManager:
    """Manage position sizing and stop loss logic."""

    def __init__(self, max_risk_pct: float = 0.1) -> None:
        self.max_risk_pct = max_risk_pct

    def calculate_order_amount(
        self,
        balance: float,
        current_price: float,
        volatility: float | None = None,
    ) -> float:
        """Return an order amount based on account balance and volatility."""

        base_amount = balance * self.max_risk_pct
        if volatility:
            adjusted = base_amount * (0.5 if volatility > 0.05 else 1.0)
            return round(adjusted, 2)
        return round(base_amount, 2)

    def check_stop_loss(
        self, entry_price: float, current_price: float, threshold: float = 0.02
    ) -> bool:
        """Return ``True`` if the stop-loss threshold is breached."""

        loss_rate = (entry_price - current_price) / entry_price
        return loss_rate >= threshold
