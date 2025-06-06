from __future__ import annotations
from datetime import datetime, timedelta


class EmotionAxis:
    """Track consecutive failures and enforce cooldown/pause rules."""

    def __init__(self) -> None:
        self.consecutive_failures = 0
        self.cooldown_until: datetime | None = None

    def record_result(self, success: bool) -> None:
        """Record condition evaluation result and update cooldown state."""
        if success:
            self.consecutive_failures = 0
            return
        self.consecutive_failures += 1
        if self.consecutive_failures >= 3:
            self.cooldown_until = datetime.utcnow() + timedelta(minutes=30)
            self.consecutive_failures = 0

    def in_cooldown(self) -> bool:
        """Return ``True`` if trading is currently paused."""
        return bool(self.cooldown_until and datetime.utcnow() < self.cooldown_until)

    def should_pause_for_greed(self, rsi: float) -> bool:
        """Return ``True`` if RSI indicates extreme greed (>85)."""
        return rsi > 85
