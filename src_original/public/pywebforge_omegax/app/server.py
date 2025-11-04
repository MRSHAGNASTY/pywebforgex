import os
import logging
from flask import Flask, render_template, send_file, jsonify
from flask_cors import CORS
from flask_sock import Sock

from .utils.paths import ensure_dirs
from .utils.logs import write_log, tail_log_lines
from .routes.api_files import files_api
from .routes.api_ai import ai_api
from .routes.api_build import build_api
from .routes.api_graphs import graphs_api
from .routes.api_plugins import plugins_api
from .routes.api_docs import docs_api
from .routes.cleanup import cleanup_bp
from .routes.health_metrics import health_bp
from .routes.sandbox_server import sandbox_server
from .routes.download import download_bp
from .routes.analyze_classify import classify_api
from .routes.sandbox_cli import sandbox_cli
from .routes.auto_ui import auto_ui

def create_app():
    ensure_dirs()
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config["SECRET_KEY"] = os.environ.get("PYWEBFORGE_SECRET", "dev-secret")
    app.logger.setLevel(logging.INFO)
    CORS(app)
    Sock(app)  # for future websocket routes

    # Blueprints
    app.register_blueprint(files_api, url_prefix="/api/files")
    app.register_blueprint(ai_api, url_prefix="/api/ai")
    app.register_blueprint(build_api, url_prefix="/api/build")
    app.register_blueprint(graphs_api, url_prefix="/api/graphs")
    app.register_blueprint(plugins_api, url_prefix="/api/plugins")
    app.register_blueprint(docs_api, url_prefix="/api/docs")
    app.register_blueprint(cleanup_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(sandbox_server, url_prefix="/api")
    app.register_blueprint(download_bp)
    app.register_blueprint(classify_api, url_prefix="/api")
    app.register_blueprint(sandbox_cli, url_prefix="/api")
    app.register_blueprint(auto_ui, url_prefix="/api")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/logs/tail")
    def tail():
        return jsonify({"success": True, "lines": tail_log_lines(250)})

    return app
