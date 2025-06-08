import json
import os
import sys
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from agents.daily_logger import DailyLogger


def test_daily_logger_write(tmp_path):
    os.environ['NOVA_LOG_DIR'] = str(tmp_path)
    logger = DailyLogger(base_dir=tmp_path)
    logger.log_failure('AgentA', 'reason')
    logger.log_success('AgentB', 'BUY', price=1.23, strategy='s', return_rate=0.1)
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    fail_file = tmp_path / 'NOVA_LOGS' / f'trade_failures_{date_str}.json'
    success_file = tmp_path / 'NOVA_LOGS' / f'trade_success_{date_str}.json'
    assert fail_file.exists()
    assert success_file.exists()
    with open(fail_file, encoding='utf-8') as f:
        data = json.loads(f.readline())
    assert data['agent'] == 'AgentA'
    with open(success_file, encoding='utf-8') as f:
        data = json.loads(f.readline())
    assert data['action'] == 'BUY'
