import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.strategy_evaluator import StrategyEvaluator


def test_evaluate_metrics():
    evaluator = StrategyEvaluator()
    returns = [0.1, -0.05, 0.2]
    trades = [
        {'market_phase': 'TREND', 'max_profit': 0.12, 'max_loss': -0.04},
        {'market_phase': 'TREND', 'max_profit': 0.2, 'max_loss': -0.05},
    ]
    res = evaluator.evaluate(returns, trades)
    assert res['total_return'] == pytest.approx(0.25)
    assert res['market_fit'] == 'TREND'

