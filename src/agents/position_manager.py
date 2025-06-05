from __future__ import annotations

"""Manage open trading positions."""


class PositionManager:
    """Manage open positions."""

    def __init__(self) -> None:
        self.positions = []

    def update(
        self, position: dict | None, entry_price: float, current_price: float
    ) -> str | None:
        """Return 'CLOSE' if exit conditions are met."""

        if not position:
            return None

        side = position.get("side", "LONG")
        if side == "LONG":
            pnl = (current_price - entry_price) / entry_price
        else:
            pnl = (entry_price - current_price) / entry_price

        if abs(pnl) >= 0.15:
            return "CLOSE"

        return None
