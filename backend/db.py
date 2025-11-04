
import sqlite3
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DB = ROOT/"backend"/"storage"/"app.db"

def get_conn():
    DB.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB)

def init_db():
    with get_conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS kv(key TEXT PRIMARY KEY, value TEXT)")
        c.commit()

def init_audit():
    with get_conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, user TEXT, role TEXT, tenant TEXT, action TEXT, resource TEXT, ok INTEGER, extra_json TEXT)")
        c.commit()

def audit_write(entry: dict):
    with get_conn() as c:
        import time, json
        c.execute("INSERT INTO audit(ts,user,role,tenant,action,resource,ok,extra_json) VALUES (?,?,?,?,?,?,?,?)",
                  (time.time(), entry.get("user"), entry.get("role"), entry.get("tenant"),
                   entry.get("action"), entry.get("resource"), 1 if entry.get("ok") else 0,
                   json.dumps(entry.get("extra",{}))))
        c.commit()
