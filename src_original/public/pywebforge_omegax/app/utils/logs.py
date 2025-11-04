import os
from datetime import datetime
from .paths import LOGS_DIR

LOG_FILE = os.path.join(LOGS_DIR, "pywebforge_ox.log")

def write_log(msg: str):
    ts = datetime.utcnow().isoformat()
    s = f"{ts} - {msg}\n"
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(s)

def tail_log_lines(n=200):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return [l.rstrip() for l in f.readlines()[-n:]]
