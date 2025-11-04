# app/core/packager.py
import zipfile
from pathlib import Path

def zipdir(src_path: str, out_zip: str) -> str:
    """
    Zip the entire folder at src_path into out_zip (path to .zip).
    Returns the path to the created zip file (string).
    """
    src = Path(src_path).resolve()
    out = Path(out_zip).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(src)))

    return str(out)
