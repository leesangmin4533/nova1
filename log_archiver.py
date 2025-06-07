import os
import zipfile
from datetime import datetime
from pathlib import Path


def archive_logs(base_dir: str = r"C:/Users/kanur/log", *, days: int = 1) -> None:
    """Compress log files older than ``days`` into per-day zip archives.

    Parameters
    ----------
    base_dir : str
        Directory containing log files.
    days : int, optional
        Minimum age of files in days before archiving, by default 1.
    """
    base = Path(base_dir)
    if not base.is_dir():
        raise FileNotFoundError(base)

    now = datetime.now()
    for file in base.iterdir():
        if not file.is_file() or file.suffix not in {".json", ".jsonl", ".csv", ".txt"}:
            continue
        age = now - datetime.fromtimestamp(file.stat().st_mtime)
        if age.days < days:
            continue
        date_str = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d")
        zip_path = base / f"{date_str}.zip"
        with zipfile.ZipFile(zip_path, "a", zipfile.ZIP_DEFLATED) as zf:
            zf.write(file, arcname=file.name)
        file.unlink()


if __name__ == "__main__":
    archive_logs()
