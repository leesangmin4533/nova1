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

