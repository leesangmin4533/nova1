"""Utilities for managing trading positions and capital."""

from typing import Optional

# Initial capital for the trading system (in KRW)
INITIAL_CAPITAL = 1_000_000

# Maximum number of simultaneous open trades
MAX_ACTIVE_TRADES = 5

# Fraction of available cash used per trade
BUY_RATE = 0.2


def can_enter_trade(active_trades):
    """Return ``True`` if a new trade can be opened."""

    return len(active_trades) < MAX_ACTIVE_TRADES


def calculate_order_amount(cash):
    """Return the order amount for a new trade given current cash."""

    return cash * BUY_RATE


def entry_block_reason(has_position: bool, confidence: Optional[float], score_percent: Optional[float]) -> Optional[str]:
    """Return a reason string if trade entry should be denied."""
    if has_position:
        return "ALREADY_IN_POSITION"
    if confidence is not None and confidence < 0.7:
        return "LOW_CONFIDENCE"
    if score_percent is not None and score_percent < 75:
        return "INSUFFICIENT_CONDITION_SCORE"
    return None


class PositionManager:
    """Manage open positions and evaluate exit conditions."""

    def __init__(self):
        self.positions = []
        self.total_buys = 0
        self.total_sells = 0

    def record_trade(self, action: str) -> None:
        """Record a buy or sell trade for analytics."""
        if action == "BUY":
            self.total_buys += 1
        elif action == "SELL":
            self.total_sells += 1

    def update(self, position, entry_price, current_price):
        """Return CLOSE if exit conditions are met."""
        if position is None:
            return None

        if current_price >= entry_price * 1.15:
            return "CLOSE"

        if current_price <= entry_price * 0.85:
            return "CLOSE"

        return None
