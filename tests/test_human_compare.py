import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.human_compare import HumanCompareAgent


def test_predict():
    agent = HumanCompareAgent()
    assert agent.predict(20) == 'BUY'
    assert agent.predict(80) == 'SELL'
    assert agent.predict(50) == 'HOLD'


def test_score_vs_human():
    agent = HumanCompareAgent()
    assert agent.score_vs_human('BUY', 'BUY') == 0
    assert agent.score_vs_human('BUY', 'SELL') == -1
