from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.activity import Activity
from models.matter import Matter
from models.client import Client
from models.time_entry import TimeEntry
from datetime import datetime

activities_bp = Blueprint("activities", __name__, url_prefix="/activities")


@activities_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "all")
    query = Activity.query.filter_by(user_id=current_user.id)
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    activities = query.order_by(Activity.created_at.desc()).all()
    
    now = datetime.utcnow()
    for act in activities:
        if act.status == 'pending' and act.started_at:
            age = now - act.started_at
            act.is_overdue = age.days >= 3
        else:
            act.is_overdue = False
            
    matters = Matter.query.filter_by(status="active").all()
    clients = Client.query.order_by(Client.name).all()
    today = datetime.utcnow().date()
    return render_template("activities.html", activities=activities, matters=matters, clients=clients, status_filter=status_filter, today=today)


@activities_bp.route("/add", methods=["POST"])
@login_required
def add():
    activity_type = request.form.get("type")
    title = request.form.get("title")
    description = request.form.get("description", "")
    matter_id = request.form.get("matter_id")
    
    date_str = request.form.get("date")
    start_time_str = request.form.get("start_time")
    end_time_str = request.form.get("end_time")

    from datetime import datetime, timedelta
    date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
    
    start_time = datetime.strptime(start_time_str, "%H:%M").time() if start_time_str else datetime.utcnow().time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time() if end_time_str else start_time

    started_at = datetime.combine(date, start_time)
    ended_at = datetime.combine(date, end_time)
    
    if ended_at < started_at:
        ended_at = ended_at + timedelta(days=1)
        
    duration = (ended_at - started_at).total_seconds() / 60

    activity = Activity(
        user_id=current_user.id,
        type=activity_type,
        title=title,
        description=description,
        source="manual",
        started_at=started_at,
        ended_at=ended_at,
        duration_minutes=duration,
        matter_id=int(matter_id) if matter_id else None,
        status="pending",
    )
    db.session.add(activity)
    db.session.commit()
    flash("Activity recorded successfully.", "success")
    return redirect(url_for("activities.index"))


@activities_bp.route("/<int:activity_id>/convert", methods=["POST"])
@login_required
def convert(activity_id):
    activity = Activity.query.get_or_404(activity_id)

    if activity.user_id != current_user.id:
        flash("Unauthorized.", "error")
        return redirect(url_for("activities.index"))

    if activity.status != "pending":
        flash("Activity already processed.", "error")
        return redirect(url_for("activities.index"))

    matter_id = request.form.get("matter_id") or activity.matter_id
    if not matter_id:
        flash("Please assign a matter before converting.", "error")
        return redirect(url_for("activities.index"))

    # Create time entry with 6-minute rounding
    time_entry = TimeEntry(
        activity_id=activity.id,
        user_id=current_user.id,
        matter_id=int(matter_id),
        date=activity.started_at.date(),
        start_time=activity.started_at.time(),
        end_time=activity.ended_at.time() if activity.ended_at else None,
        description=f"{activity.type.title()}: {activity.title}",
        duration_minutes=activity.duration_minutes,
        rate=current_user.hourly_rate,
        units=0,
        amount=0,
        status="draft",
    )
    time_entry.compute_billing()

    activity.status = "converted"
    activity.matter_id = int(matter_id)

    db.session.add(time_entry)
    db.session.commit()

    flash(f"Activity converted to time entry ({time_entry.units} units, R{time_entry.amount:.2f}).", "success")
    return redirect(url_for("activities.index"))


@activities_bp.route("/<int:activity_id>/dismiss", methods=["POST"])
@login_required
def dismiss(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    if activity.user_id != current_user.id:
        flash("Unauthorized.", "error")
        return redirect(url_for("activities.index"))

    activity.status = "dismissed"
    db.session.commit()
    flash("Activity dismissed.", "info")
    return redirect(url_for("activities.index"))
