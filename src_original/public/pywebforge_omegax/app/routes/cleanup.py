import time, shutil
from flask import Blueprint, jsonify
from ..core.settings import TMP_ROOT, MAX_AGE_HOURS
cleanup_bp=Blueprint("cleanup_bp", __name__)
@cleanup_bp.post("/admin/cleanup")
def cleanup():
    now=time.time(); cutoff=now-MAX_AGE_HOURS*3600; removed=[]
    for d in TMP_ROOT.glob("*"):
        try:
            if d.is_dir() and d.stat().st_mtime < cutoff:
                shutil.rmtree(d, ignore_errors=True); removed.append(str(d))
        except Exception: pass
    return jsonify({"success": True, "removed": removed})
