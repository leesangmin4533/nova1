from pathlib import Path
import os

# Log directory
LOG_BASE_DIR = Path(os.environ.get("NOVA_LOG_DIR", r"C:/Users/kanur/log"))

# Optional HTML UI file path
UI_PATH = LOG_BASE_DIR / "UI" / "live_nova_decision_emotion_ui.html"

# ngrok settings
USE_NGROK = os.environ.get("USE_NGROK", "True") == "True"
NGROK_PORT = int(os.environ.get("NGROK_PORT", "5000"))

# Local status server port
LOCAL_SERVER_PORT = int(os.environ.get("LOCAL_SERVER_PORT", "5000"))
