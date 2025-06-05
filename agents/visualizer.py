from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class VisualizerAgent:
    """Placeholder for UI integration."""

    def update(self, data: Dict[str, Any]) -> None:
        # This agent would push updates to a UI framework.
        pass
