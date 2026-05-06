from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db
from models.activity import Activity
from models.time_entry import TimeEntry
from models.invoice import Invoice
from models.matter import Matter
from models.client import Client
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    today = datetime.utcnow().date()
    week_start = today - timedelta(days=today.weekday())

    # Stats
    total_hours_today = db.session.query(
        func.coalesce(func.sum(TimeEntry.duration_minutes), 0)
    ).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date == today,
    ).scalar() / 60

    total_hours_week = db.session.query(
        func.coalesce(func.sum(TimeEntry.duration_minutes), 0)
    ).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= week_start,
    ).scalar() / 60

    pending_entries = TimeEntry.query.filter_by(
        user_id=current_user.id, status="draft"
    ).count()

    billable_amount_week = db.session.query(
        func.coalesce(func.sum(TimeEntry.amount), 0)
    ).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= week_start,
    ).scalar()

    active_matters = Matter.query.filter_by(status="active").count()
    total_clients = Client.query.count()

    pending_activities = Activity.query.filter_by(
        user_id=current_user.id, status="pending"
    ).count()

    total_invoices = Invoice.query.count()
    total_billed = db.session.query(
        func.coalesce(func.sum(Invoice.total), 0)
    ).scalar()

    # Recent activities
    recent_activities = Activity.query.filter_by(
        user_id=current_user.id
    ).order_by(Activity.created_at.desc()).limit(5).all()

    # Daily hours for the last 7 days (for chart)
    daily_hours = []
    daily_labels = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        hours = db.session.query(
            func.coalesce(func.sum(TimeEntry.duration_minutes), 0)
        ).filter(
            TimeEntry.user_id == current_user.id,
            TimeEntry.date == d,
        ).scalar() / 60
        daily_hours.append(round(hours, 1))
        daily_labels.append(d.strftime("%a"))

    return render_template(
        "dashboard.html",
        total_hours_today=round(total_hours_today, 1),
        total_hours_week=round(total_hours_week, 1),
        pending_entries=pending_entries,
        billable_amount_week=round(billable_amount_week, 2),
        active_matters=active_matters,
        total_clients=total_clients,
        pending_activities=pending_activities,
        total_invoices=total_invoices,
        total_billed=round(total_billed, 2),
        recent_activities=recent_activities,
        daily_hours=daily_hours,
        daily_labels=daily_labels,
    )
