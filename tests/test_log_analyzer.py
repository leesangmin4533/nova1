import os
import sys
import json
import tempfile

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from log_analyzer import analyze_logs


def create_log(directory, idx, action, price, return_rate):
    data = {
        "timestamp": "2021-01-01T00:00:00",
        "agent": "EntryDecisionAgent",
        "action": action,
        "price": price,
        "return_rate": return_rate,
    }
    filename = os.path.join(directory, f"log_{idx}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f)


def test_analyze_logs_basic(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    create_log(log_dir, 1, "BUY", 100, 0.0)
    create_log(log_dir, 2, "SELL", 110, 0.1)
    create_log(log_dir, 3, "BUY", 200, 0.0)
    create_log(log_dir, 4, "SELL", 180, -0.1)

    result = analyze_logs(str(log_dir))

    assert result["buys"] == 2
    assert result["sells"] == 2
    assert result["average_return"] == pytest.approx(0.0)
    assert result["cumulative_return"] == pytest.approx(-0.01)
    assert result["win_rate"] == pytest.approx(0.5)
