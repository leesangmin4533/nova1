from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class LogRecord:
    timestamp: float
    agent: str
    action: str
    price: float
    confidence: float


class LoggerAgent:
    def __init__(self, log_dir: str = "log") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(level=logging.INFO)

    def log(self, record: LogRecord) -> None:
        path = self.log_dir / f"{int(record.timestamp)}.json"
        with path.open("a", encoding="utf-8") as f:
            json.dump(asdict(record), f)
            f.write("\n")
        logging.info("%s: %s", record.agent, record.action)
