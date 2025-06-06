import os
import sys
import math
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.market_sentiment import MarketSentimentAgent


def test_calc_rsi_insufficient_data():
    agent = MarketSentimentAgent()
    closes = [1, 2, 3]
    assert agent.calc_rsi(closes, period=5) == 50.0


def test_calc_rsi_zero_loss():
    agent = MarketSentimentAgent()
    closes = list(range(1, 22))  # strictly increasing
    assert agent.calc_rsi(closes, period=20) == 100.0


def test_calc_rsi_general_case():
    agent = MarketSentimentAgent()
    closes = [1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 13, 14, 15, 16, 17]
    rsi = agent.calc_rsi(closes, period=20)
    assert math.isclose(rsi, 90.0, abs_tol=1e-6)
