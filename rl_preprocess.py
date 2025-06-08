import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from config import LOG_BASE_DIR


def preprocess_logs(base_dir: str | Path = LOG_BASE_DIR) -> Path:
    """Convert judgment logs into RL format and save to a jsonl file.

    The output file will be named ``nova_rl_data_{YYYY-MM-DD}.jsonl`` under
    ``강화학습전처리`` inside ``base_dir``.
    """
    base_path = Path(base_dir) / "판단기록"
    out_dir = Path(base_dir) / "강화학습전처리"
    out_dir.mkdir(parents=True, exist_ok=True)

    rl_entries: List[Dict[str, Any]] = []
    files = sorted(base_path.glob("log_*.jsonl"))
    for file in files:
        with open(file, encoding="utf-8") as f:
            raw = [json.loads(line) for line in f if line.strip()]
        for i, entry in enumerate(raw):
            state = [
                entry.get("rsi"),
                entry.get("ma_diff"),
                entry.get("volume_ratio"),
                entry.get("golden_cross_dist"),
                entry.get("market_emotion_index", 0.0),
            ]
            action_map = {"BUY": 1, "SELL": -1, "NONE": 0}
            action = action_map.get(entry.get("action", "NONE"), 0)
            change = entry.get("future_return_5m", 0.0)
            reward = 0
            if change > 0.015:
                reward = 1
            elif change < -0.015:
                reward = -1
            next_state = None
            if i + 1 < len(raw):
                nxt = raw[i + 1]
                next_state = [
                    nxt.get("rsi"),
                    nxt.get("ma_diff"),
                    nxt.get("volume_ratio"),
                    nxt.get("golden_cross_dist"),
                    nxt.get("market_emotion_index", 0.0),
                ]
            done = i + 1 == len(raw)
            rl_entries.append(
                {
                    "state": state,
                    "action": action,
                    "reward": reward,
                    "next_state": next_state,
                    "done": done,
                }
            )

    date_str = datetime.now().strftime("%Y-%m-%d")
    out_file = out_dir / f"nova_rl_data_{date_str}.jsonl"
    with open(out_file, "w", encoding="utf-8") as f:
        for e in rl_entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return out_file


if __name__ == "__main__":
    path = preprocess_logs()
    print(f"saved {path}")
