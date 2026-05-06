import random
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db
from models.activity import Activity
from models.matter import Matter
from datetime import datetime, timedelta

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Simulated activity templates
ACTIVITY_TEMPLATES = [
    {"type": "email", "title": "Review client correspondence - {matter}", "duration": (5, 25)},
    {"type": "email", "title": "Draft response to opposing counsel - {matter}", "duration": (10, 35)},
    {"type": "email", "title": "Send update to client regarding {matter}", "duration": (5, 15)},
    {"type": "meeting", "title": "Client consultation - {matter}", "duration": (30, 90)},
    {"type": "meeting", "title": "Internal case strategy meeting - {matter}", "duration": (20, 60)},
    {"type": "meeting", "title": "Settlement discussion - {matter}", "duration": (30, 120)},
    {"type": "call", "title": "Phone call with client re: {matter}", "duration": (5, 30)},
    {"type": "call", "title": "Conference call - opposing counsel - {matter}", "duration": (15, 45)},
    {"type": "document", "title": "Draft contract for {matter}", "duration": (30, 120)},
    {"type": "document", "title": "Review and amend agreement - {matter}", "duration": (20, 90)},
    {"type": "document", "title": "Prepare court submissions - {matter}", "duration": (45, 180)},
    {"type": "document", "title": "Draft letter of demand - {matter}", "duration": (15, 45)},
    {"type": "research", "title": "Legal research - case law for {matter}", "duration": (30, 120)},
    {"type": "research", "title": "Statutory research re: {matter}", "duration": (20, 60)},
]

SOURCES = ["outlook", "teams", "auto-detect"]


@api_bp.route("/simulate-activity", methods=["POST"])
@login_required
def simulate_activity():
    """Simulate auto-detected activities for demo purposes."""
    matters = Matter.query.filter_by(status="active").all()
    if not matters:
        return jsonify({"error": "No active matters. Please add clients and matters first."}), 400

    count = int(request.json.get("count", 1)) if request.is_json else 1
    count = min(count, 5)

    created = []
    for _ in range(count):
        template = random.choice(ACTIVITY_TEMPLATES)
        matter = random.choice(matters)
        dur_min, dur_max = template["duration"]
        duration = random.randint(dur_min, dur_max)

        now = datetime.utcnow()
        started = now - timedelta(minutes=random.randint(30, 480))
        ended = started + timedelta(minutes=duration)

        activity = Activity(
            user_id=current_user.id,
            type=template["type"],
            title=template["title"].format(matter=matter.title),
            description=f"Auto-detected activity for {matter.reference}",
            source=random.choice(SOURCES),
            started_at=started,
            ended_at=ended,
            duration_minutes=duration,
            matter_id=matter.id,
            status="pending",
        )
        db.session.add(activity)
        created.append({"type": activity.type, "title": activity.title, "duration": duration})

    db.session.commit()
    return jsonify({"message": f"{len(created)} activities detected", "activities": created})


@api_bp.route("/dashboard-stats")
@login_required
def dashboard_stats():
    """Return dashboard stats as JSON for AJAX refresh."""
    from models.time_entry import TimeEntry
    from sqlalchemy import func
    today = datetime.utcnow().date()

    hours_today = db.session.query(
        func.coalesce(func.sum(TimeEntry.duration_minutes), 0)
    ).filter(TimeEntry.user_id == current_user.id, TimeEntry.date == today).scalar() / 60

    pending = Activity.query.filter_by(user_id=current_user.id, status="pending").count()

    return jsonify({"hours_today": round(hours_today, 1), "pending_activities": pending})
