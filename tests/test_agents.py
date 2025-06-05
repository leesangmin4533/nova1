import os
import json
from pathlib import Path

import pytest

from src.agents.market_sentiment import MarketSentimentAgent
from src.agents.strategy_selector import StrategySelector
from src.agents.entry_decision import EntryDecisionAgent
from src.agents.position_manager import PositionManager
from src.agents.logger_agent import LoggerAgent
from src.agents.learning_agent import LearningAgent


def test_market_sentiment():
    agent = MarketSentimentAgent()
    candle = {
        "close": list(range(100, 120)),
        "volume": [100] * 19 + [150],
    }
    book = {"bid": 70, "ask": 30}
    sentiment = agent.update(candle, book, 1.0)
    assert sentiment == "EXTREME_GREED"

    candle = {
        "close": list(range(120, 100, -1)),
        "volume": [100] * 19 + [50],
    }
    book = {"bid": 30, "ask": 70}
    sentiment = agent.update(candle, book, -1.0)
    assert sentiment == "EXTREME_FEAR"


def test_strategy_selector():
    selector = StrategySelector()
    strat = selector.select("EXTREME_FEAR")
    assert strat[0] == "reversal"
    strat = selector.select("GREED")
    assert strat[0] == "momentum"


def test_entry_decision():
    agent = EntryDecisionAgent()
    closes = [1] * 15 + [2, 3, 4, 5, 6]
    chart = {"close": closes}
    signal = agent.evaluate(("trend_follow", {}), chart, None)
    assert signal == "BUY"

    closes = list(range(20, 0, -1))
    chart = {"close": closes}
    signal = agent.evaluate(("trend_follow", {}), chart, None)
    assert signal == "SELL"


def test_position_manager():
    manager = PositionManager()
    assert manager.update("LONG", 100, 120) == "CLOSE"
    assert manager.update("LONG", 100, 80) == "CLOSE"
    assert manager.update("LONG", 100, 105) is None


def test_logger_agent(tmp_path):
    logger = LoggerAgent(log_dir=tmp_path)
    logger.log("EntryDecisionAgent", "BUY", price=100, confidence=0.8)
    files = list(Path(tmp_path).iterdir())
    assert len(files) == 1
    data = json.loads(files[0].read_text())
    assert data["agent"] == "EntryDecisionAgent"
    assert data["action"] == "BUY"


def test_learning_agent():
    learner = LearningAgent()
    history = [
        {"strategy_id": "trend_follow", "return": 0.1},
        {"strategy_id": "trend_follow", "return": 0.2},
        {"strategy_id": "swing", "return": -0.1},
    ]
    weights = learner.update(history)
    assert pytest.approx(weights["trend_follow"], 0.01) == 0.15
    assert pytest.approx(weights["swing"], 0.01) == -0.1
