from flask import Blueprint, request, jsonify
auto_ui = Blueprint('auto_ui', __name__)

@auto_ui.get('/auto_ui/<path:filepath>')
def open_auto_ui(filepath: str):
    project = request.args.get('project', '')
    return jsonify({'success': True, 'mode': 'web', 'file': filepath, 'project': project})
