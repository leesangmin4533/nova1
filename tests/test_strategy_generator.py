import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.strategy_generator import StrategyGenerator


def test_create_strategy():
    gen = StrategyGenerator(seed=42)
    strat = gen.create_strategy()
    assert 'conditions' in strat
    assert isinstance(strat['conditions'], list)
    assert strat['id'].startswith('gen_')
