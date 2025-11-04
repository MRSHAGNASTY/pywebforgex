"""Auto-fix missing dependency by suggesting pip install."""

def detect_and_fix(import_name: str):
    try:
        __import__(import_name)
        return {"status":"present"}
    except Exception:
        return {"status":"missing", "fix":"pip install "+import_name}
