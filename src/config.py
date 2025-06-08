from __future__ import annotations
import os
from pathlib import Path

LOG_BASE_DIR = Path(os.environ.get('NOVA_LOG_DIR', Path.home() / 'nova_logs'))
