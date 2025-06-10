from __future__ import annotations
import os
from pathlib import Path

# Base directory for all log files.  The location can be overridden by setting
# the ``NOVA_LOG_DIR`` environment variable.  When not provided, it defaults to
# ``C:/Users/kanur/log`` to match the behaviour of ``config.py`` in the project
# root.  Using ``Path`` ensures compatibility across platforms.
LOG_BASE_DIR = Path(os.environ.get("NOVA_LOG_DIR", r"C:/Users/kanur/log"))

# Optional path to the legacy HTML UI.  This file is opened automatically by the
# status server if present.
UI_PATH = LOG_BASE_DIR / "UI" / "live_nova_decision_emotion_ui.html"

# Port used by the local Flask status server.  The value may be overridden via
# the ``LOCAL_SERVER_PORT`` environment variable.
LOCAL_SERVER_PORT = int(os.environ.get("LOCAL_SERVER_PORT", "5000"))
