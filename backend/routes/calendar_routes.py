from flask import Blueprint, request, jsonify
from models.user import User
from db import db
from services.ms_graph import get_calendar_events, create_calendar_event

calendar_bp = Blueprint("calendar", __name__, url_prefix="/api/calendar")

@calendar_bp.route("/events", methods=["GET"])
def list_events():
    email = request.args.get("email")
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    events = get_calendar_events(user)
    return jsonify(events)

@calendar_bp.route("/events", methods=["POST"])
def create_event():
    email = request.json.get("email")
    event_data = request.json.get("event")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    response = create_calendar_event(user, event_data)
    return jsonify(response)

@calendar_bp.route("/events", methods=["GET"]) #TODO: add login required to ensure access control
def get_calendar_events():
    access_token = get_access_token(current_user)  # Retrieve the access token for the current user

    # Request to Microsoft Graph API
    graph_url = 'https://graph.microsoft.com/v1.0/me/events'
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.get(graph_url, headers=headers)

    if response.status_code == 200:
        events = response.json()['value']
        return jsonify(events)
    else:
        return jsonify({"error": "Failed to fetch calendar events"}), 500

