import os
import pytest

@pytest.fixture(autouse=True)
def _set_nova_log_dir(tmp_path, monkeypatch):
    monkeypatch.setenv('NOVA_LOG_DIR', str(tmp_path))
    yield

