import yaml
from typing import Any, Dict


class ConfigLoader:
    """Load configuration for NOVA trading framework."""

    def __init__(self, path: str = "kodex_config.yaml"):
        self.path = path
        self.config: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        with open(self.path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        return self.config
