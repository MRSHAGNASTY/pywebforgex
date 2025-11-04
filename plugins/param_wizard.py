"""Parameter wizard with validation."""

def make_config(path: str, retries: int = 3, debug: bool = False):
    assert isinstance(path, str) and path, "path required"
    assert isinstance(retries, int) and retries>=0
    return {"path": path, "retries": retries, "debug": bool(debug)}
