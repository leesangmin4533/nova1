import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.logger_agent import LoggerAgent


def test_log_judgment(tmp_path):
    os.environ['NOVA_LOG_DIR'] = str(tmp_path)
    logger = LoggerAgent(log_dir=tmp_path)
    logger.log_judgment(
        action='BUY',
        reason='test',
        indicators={'rsi': 50},
        market_emotion='NEUTRAL',
        human_likely_action='HOLD',
        score_vs_human=0,
        strategy_version='v1',
        conflict_analysis={'conflict_index': 0.5, 'conflict_factors': []},
    )
    date_str = Path(logger._judgment_file_for_today()).name
    path = tmp_path / '판단로그' / date_str
    assert path.exists()
    with open(path, encoding='utf-8') as f:
        data = json.loads(f.readline())
    assert data['action'] == 'BUY'
    assert data['strategy_version'] == 'v1'
    assert 'conflict_analysis' in data
