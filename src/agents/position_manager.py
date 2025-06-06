"""Utilities for managing trading positions and capital."""

from typing import Optional

# Initial capital for the trading system (in KRW)
INITIAL_CAPITAL = 1_000_000

# Maximum number of simultaneous open trades
MAX_ACTIVE_TRADES = 5

# Fraction of available cash used per trade (max 10% of balance)
BUY_RATE = 0.1


def can_enter_trade(active_trades):
    """Return ``True`` if a new trade can be opened."""

    return len(active_trades) < MAX_ACTIVE_TRADES


def calculate_order_amount(cash, recent_volatility: float | None = None):
    """Return the order amount for a new trade given current cash.

    When ``recent_volatility`` is provided, the amount is scaled down as
    volatility increases to reduce risk exposure.
    """

    amount = cash * BUY_RATE
    if recent_volatility is not None:
        factor = max(0.5, 1 - recent_volatility * 50)
        amount *= factor
    return amount


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
        """Evaluate open position and return action.

        - Profit >= 3%   -> ``CLOSE``
        - Loss <= -2%    -> ``PARTIAL_CLOSE`` on first trigger, ``CLOSE`` if
          already reduced.
        """

        if position is None:
            return None

        change = (current_price - entry_price) / entry_price

        if change >= 0.03:
            return "CLOSE"

        if change <= -0.02:
            if not position.get("half_closed"):
                position["quantity"] *= 0.5
                position["half_closed"] = True
                return "PARTIAL_CLOSE"
            return "CLOSE"

        return None
