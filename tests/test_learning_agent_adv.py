import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.learning_agent import LearningAgent


def test_learning_agent_update(tmp_path):
    state = tmp_path / 'state.json'
    agent = LearningAgent(state_path=state)
    agent.record_trade('s1', 0.1, market_phase='TREND', emotion_score=0.5, risk=0.1)
    agent.record_trade('s1', 0.05, market_phase='TREND', emotion_score=0.4, risk=0.1)
    weights = agent.update()
    assert 's1' in weights
    assert weights['s1'] > 0

