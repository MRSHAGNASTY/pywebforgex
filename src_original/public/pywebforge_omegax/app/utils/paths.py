import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "..", "projects")
GENERATED_DIR = os.path.join(BASE_DIR, "..", "generated")
LOGS_DIR = os.path.join(BASE_DIR, "..", "logs")

def ensure_dirs():
    for p in [UPLOAD_DIR, GENERATED_DIR, LOGS_DIR]:
        os.makedirs(p, exist_ok=True)
