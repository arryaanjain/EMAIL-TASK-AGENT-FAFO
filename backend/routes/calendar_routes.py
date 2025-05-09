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
