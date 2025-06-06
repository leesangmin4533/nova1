import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.session_logger import SessionLogger


def test_session_logger(tmp_path):
    logger = SessionLogger(base_dir=tmp_path)
    logger.log_success('A', 'BUY', price=1.0, strategy='s', return_rate=0.1)
    logger.log_failure('B', 'error')
    logger.log_hold('C')

    log_files = list((tmp_path / 'NOVA_LOGS').glob('trade_log_*.json'))
    assert len(log_files) == 1
    with open(log_files[0], encoding='utf-8') as f:
        lines = [json.loads(line) for line in f.read().splitlines()]
    assert lines[0]['action'] == 'BUY'
    assert lines[1]['action'] == 'FAILURE'
    assert lines[2]['action'] == 'HOLD'
