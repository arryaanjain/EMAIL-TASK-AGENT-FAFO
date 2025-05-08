from flask import Flask, request, jsonify
from pipeline.email_pipeline import run_email_pipeline
from utils.email_reader import fetch_unread_emails
import json
import re
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

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

            # Remove code fences and any extra text
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

if __name__ == '__main__':
    app.run(debug=True)
