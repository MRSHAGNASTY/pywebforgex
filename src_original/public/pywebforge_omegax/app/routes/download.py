from flask import Blueprint, request, send_file, abort
import os, tempfile
download_bp=Blueprint('download_bp', __name__)
@download_bp.get('/download')
def download():
    p=request.args.get('path')
    if not p or not os.path.exists(p): return abort(404)
    tmp=tempfile.gettempdir()
    if not os.path.abspath(p).startswith(tmp): return abort(403)
    return send_file(p, as_attachment=True)
