"""OpsPortal Flask HTTP application."""

import os
import subprocess
from typing import Optional

from flask import Flask, Response, jsonify, request

from app.auth import SESSION_SECRET, authenticate_user, init_db, lookup_user
from app.diagnostics import resolve_host
from app.files import DEFAULT_REPORTS_DIR, read_report
from app.profiles import parse_profile_config
from app.templates_view import render_greeting_banner


def create_app(
    db_path: Optional[str] = None,
    reports_dir: str = DEFAULT_REPORTS_DIR,
) -> Flask:
    """Create and configure the OpsPortal Flask app."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SESSION_SECRET
    resolved_db = db_path or os.environ.get("OPSPORTAL_DB", "data/opsportal.db")
    init_db(resolved_db)

    @app.get("/health")
    def health() -> Response:
        return jsonify({"status": "ok"})

    @app.post("/api/login")
    def login():
        body = request.get_json(silent=True) or {}
        username = body.get("username", "")
        password = body.get("password", "")
        if not username or not password:
            return jsonify({"error": "username and password are required"}), 400

        user = authenticate_user(resolved_db, username, password)
        if user is None:
            return jsonify({"error": "invalid credentials"}), 401
        return jsonify({"user": user}), 200

    @app.get("/api/users")
    def get_user():
        username = request.args.get("username", "")
        if not username:
            return jsonify({"error": "username query parameter is required"}), 400

        user = lookup_user(resolved_db, username)
        if user is None:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"user": user}), 200

    @app.get("/api/reports/download")
    def download_report():
        filename = request.args.get("name", "")
        if not filename:
            return jsonify({"error": "name query parameter is required"}), 400
        try:
            content = read_report(filename, reports_dir=reports_dir)
        except FileNotFoundError:
            return jsonify({"error": "report not found"}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 400
        return Response(content, mimetype="text/plain")

    @app.get("/api/diagnostics/host")
    def diagnostics_host():
        host = request.args.get("host", "")
        if not host:
            return jsonify({"error": "host query parameter is required"}), 400
        try:
            result = resolve_host(host)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            return jsonify({"error": f"lookup failed: {exc}"}), 500
        return jsonify({"host": host, "result": result}), 200

    @app.get("/api/greeting")
    def greeting():
        name = request.args.get("name", "Operator")
        html = render_greeting_banner(name)
        return Response(html, mimetype="text/html")

    @app.post("/api/profiles/import")
    def import_profile():
        raw_yaml = request.get_data(as_text=True)
        if not raw_yaml.strip():
            return jsonify({"error": "YAML body is required"}), 400
        try:
            profile = parse_profile_config(raw_yaml)
        except Exception as exc:
            return jsonify({"error": f"invalid profile YAML: {exc}"}), 400
        return jsonify({"profile": profile}), 200

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host="127.0.0.1", port=8080, debug=False)
