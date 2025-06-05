"""Position monitoring agent."""

from __future__ import annotations


class PositionManager:
    """Manage open positions."""

    def __init__(self) -> None:
        self.positions = []

    def update(self, position: str, entry_price: float, current_price: float):
        """Return CLOSE if exit conditions are met."""
        if position is None:
            return None
        pnl = (current_price - entry_price) / entry_price
        if pnl >= 0.15 or pnl <= -0.15:
            return "CLOSE"
        return None
