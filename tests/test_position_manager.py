import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from agents.position_manager import PositionManager


def test_close_on_profit():
    pm = PositionManager()
    action = pm.update({'quantity': 1}, entry_price=100, current_price=103)
    assert action == 'CLOSE'


def test_partial_then_close_on_loss():
    pm = PositionManager()
    pos = {'quantity': 1}
    action = pm.update(pos, entry_price=100, current_price=98)
    assert action == 'PARTIAL_CLOSE'
    assert pos['quantity'] == 0.5
    action = pm.update(pos, entry_price=100, current_price=97)
    assert action == 'CLOSE'


def test_no_close_within_bounds():
    pm = PositionManager()
    action = pm.update({'quantity': 1}, entry_price=100, current_price=100)
    assert action is None


def test_none_position():
    pm = PositionManager()
    action = pm.update(None, entry_price=100, current_price=120)
    assert action is None

