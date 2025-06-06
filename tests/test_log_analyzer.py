import os
import sys
import math
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from log_analyzer import load_logs, analyze_logs, get_recent_logs, trade_returns


def test_load_and_analyze_logs():
    log_dir = os.path.join(os.path.dirname(__file__), 'sample_logs')
    logs = load_logs(log_dir)
    assert len(logs) == 4

    stats = analyze_logs(logs)
    assert stats['total_trades'] == 4
    assert stats['agent_counts']['EntryDecisionAgent'] == 3
    assert math.isclose(stats['average_return'], 0.05, rel_tol=1e-9)
    assert math.isclose(stats['cumulative_return'], 0.2, rel_tol=1e-9)
    assert stats['max_return'] == 0.2
    assert stats['min_return'] == -0.1
    assert math.isclose(stats['strategy_win_rates']['trend_follow'], 1.0)
    assert math.isclose(stats['strategy_win_rates']['momentum'], 0.0)


def test_get_recent_logs():
    log_dir = os.path.join(os.path.dirname(__file__), 'sample_logs')
    logs = load_logs(log_dir)
    recent = get_recent_logs(logs, n=2)
    assert len(recent) == 2
    assert recent[-1]['timestamp'] == '2024-01-01T00:30:00'


def test_trade_returns():
    log_dir = os.path.join(os.path.dirname(__file__), 'sample_logs')
    logs = load_logs(log_dir)
    returns, cumulative = trade_returns(logs)
    assert returns == [0.1, 0.2, -0.1]
    assert math.isclose(cumulative[-1], 0.2, rel_tol=1e-9)
