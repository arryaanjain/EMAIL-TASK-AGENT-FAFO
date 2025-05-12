from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import json
import re
import os

# Load environment variables from .env
load_dotenv()

# App modules
from config import Config
from db import db
from pipeline.email_pipeline import run_email_pipeline
from utils.email_reader import fetch_unread_emails

# Blueprints
from routes.auth_routes import auth_bp
from routes.calendar_routes import calendar_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "super-secret-and-unique-key"
    CORS(app)

    # Load configuration
    app.config.from_object(Config)

    # Initialize DB
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(calendar_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    # Legacy Routes (Consider moving to blueprints later)
    @app.route('/api/summarize_email', methods=['POST'])
    def summarize_email():
        data = request.get_json()
        subject = data.get("subject")
        body = data.get("body")
        result = run_email_pipeline(subject, body)

        try:
            json_result = json.loads(result)
            return jsonify(json_result)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON from agent"}), 500

    @app.route("/api/process_emails", methods=["GET"])
    def process_emails():
        emails = fetch_unread_emails()
        results = []

        for subject, body in emails:
            try:
                result = run_email_pipeline(subject, body)
                result_cleaned = re.search(r'\{.*\}', result, re.DOTALL)

                if result_cleaned:
                    json_result = json.loads(result_cleaned.group())
                    results.append(json_result)
                else:
                    raise json.JSONDecodeError("No JSON object found", result, 0)

            except json.JSONDecodeError:
                results.append({
                    "subject": subject,
                    "error": "Invalid JSON from agent"
                })

        return jsonify(results)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
