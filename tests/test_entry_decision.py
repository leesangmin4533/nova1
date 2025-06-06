import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from agents.entry_decision import EntryDecisionAgent


def test_golden_cross_buy():
    agent = EntryDecisionAgent()
    chart_data = [1] * 21 + [2] * 5
    assert agent.evaluate("momentum", chart_data, None) == "BUY"


def test_golden_cross_requires_length():
    agent = EntryDecisionAgent()
    chart_data = [1] * 20 + [2] * 4
    assert agent.evaluate("momentum", chart_data, None) == "HOLD"


def test_orderbook_weighted_buy():
    agent = EntryDecisionAgent()
    order_book = {
        "bids": [{"price": 100, "volume": 2}] * 10,
        "asks": [{"price": 99, "volume": 1}] * 10,
    }
    chart = [1] * 25
    res = agent.evaluate(("orderbook_weighted", {}), chart, None, order_book)
    assert isinstance(res, dict)
    assert res["signal"] == "BUY"


def test_orderbook_weighted_sell():
    agent = EntryDecisionAgent()
    order_book = {
        "bids": [{"price": 100, "volume": 1}] * 10,
        "asks": [{"price": 101, "volume": 2}] * 10,
    }
    chart = [1] * 25
    res = agent.evaluate(("orderbook_weighted", {}), chart, None, order_book)
    assert isinstance(res, dict)
    assert res["signal"] == "SELL"


def test_nearest_failed_condition():
    agent = EntryDecisionAgent()
    chart = [100] * 20 + [100.5, 100, 100.4, 99.8, 100.2]
    result = agent.evaluate("momentum", chart, None)
    assert result == "HOLD"
    nf = agent.nearest_failed
    assert nf["condition"] == "rsi_above_55"
    assert nf["passed"] is False
    assert nf["diff"] == pytest.approx(-0.83, abs=0.1)

