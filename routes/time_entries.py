from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.time_entry import TimeEntry
from models.matter import Matter

time_entries_bp = Blueprint("time_entries", __name__, url_prefix="/time-entries")


@time_entries_bp.route("/")
@login_required
def index():
    status_filter = request.args.get("status", "all")
    query = TimeEntry.query.filter_by(user_id=current_user.id)
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    entries = query.order_by(TimeEntry.date.desc(), TimeEntry.created_at.desc()).all()
    matters = Matter.query.filter_by(status="active").all()
    return render_template("time_entries.html", entries=entries, matters=matters, status_filter=status_filter)


@time_entries_bp.route("/add", methods=["POST"])
@login_required
def add():
    matter_id = request.form.get("matter_id")
    description = request.form.get("description")
    duration = float(request.form.get("duration") or 0)
    date_str = request.form.get("date")
    start_time_str = request.form.get("start_time")
    end_time_str = request.form.get("end_time")

    from datetime import datetime
    date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
    
    start_time = datetime.strptime(start_time_str, "%H:%M").time() if start_time_str else None
    end_time = datetime.strptime(end_time_str, "%H:%M").time() if end_time_str else None

    if duration == 0 and start_time and end_time:
        t1 = datetime.combine(date, start_time)
        t2 = datetime.combine(date, end_time)
        duration = (t2 - t1).total_seconds() / 60

    entry = TimeEntry(
        user_id=current_user.id,
        matter_id=int(matter_id),
        date=date,
        start_time=start_time,
        end_time=end_time,
        description=description,
        duration_minutes=duration,
        rate=current_user.hourly_rate,
        units=0,
        amount=0,
        status="draft",
    )
    entry.compute_billing()

    db.session.add(entry)
    db.session.commit()
    flash(f"Time entry added ({entry.units} units, R{entry.amount:.2f}).", "success")
    return redirect(url_for("time_entries.index"))


@time_entries_bp.route("/<int:entry_id>/approve", methods=["POST"])
@login_required
def approve(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id and current_user.role != "manager":
        flash("Unauthorized.", "error")
        return redirect(url_for("time_entries.index"))

    entry.status = "approved"
    db.session.commit()
    flash("Time entry approved.", "success")
    return redirect(url_for("time_entries.index"))


@time_entries_bp.route("/<int:entry_id>/edit", methods=["POST"])
@login_required
def edit(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("Unauthorized.", "error")
        return redirect(url_for("time_entries.index"))

    entry.description = request.form.get("description", entry.description)
    entry.duration_minutes = float(request.form.get("duration", entry.duration_minutes))
    matter_id = request.form.get("matter_id")
    if matter_id:
        entry.matter_id = int(matter_id)
    entry.compute_billing()
    db.session.commit()
    flash("Time entry updated.", "success")
    return redirect(url_for("time_entries.index"))


@time_entries_bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash("Unauthorized.", "error")
        return redirect(url_for("time_entries.index"))

    if entry.status == "billed":
        flash("Cannot delete billed entries.", "error")
        return redirect(url_for("time_entries.index"))

    db.session.delete(entry)
    db.session.commit()
    flash("Time entry deleted.", "info")
    return redirect(url_for("time_entries.index"))


@time_entries_bp.route("/approve-all", methods=["POST"])
@login_required
def approve_all():
    entries = TimeEntry.query.filter_by(user_id=current_user.id, status="draft").all()
    for entry in entries:
        entry.status = "approved"
    db.session.commit()
    flash(f"{len(entries)} entries approved.", "success")
    return redirect(url_for("time_entries.index"))
