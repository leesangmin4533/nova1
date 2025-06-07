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
    assert res["signal"] == "HOLD"


def test_nearest_failed_condition():
    agent = EntryDecisionAgent()
    chart = [100] * 20 + [100.5, 100, 100.4, 99.8, 100.2]
    result = agent.evaluate("momentum", chart, None)
    assert result == "BUY"
    nf = agent.nearest_failed
    assert nf["condition"] == "orderbook_bias_up"
    assert nf["passed"] is False


def test_decide_entry_override():
    agent = EntryDecisionAgent()
    agent.failed_conditions = ["orderbook_bias_up"]
    allow, reason = agent.decide_entry("BUY", "INSUFFICIENT_CONDITION_SCORE", 72)
    assert allow is True
    assert reason == "high_score_override"


def test_conflict_index_detection():
    agent = EntryDecisionAgent()
    chart = [1] * 21 + [2] * 5
    order_book = {"bid_volume": 1, "ask_volume": 10, "bids": [], "asks": []}
    signal = agent.evaluate("momentum", chart, None, order_book)
    assert signal == "HOLD"
    ci = agent.last_conflict["conflict_index"]
    assert ci >= 0.5

