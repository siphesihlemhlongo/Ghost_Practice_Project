from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.client import Client
from models.matter import Matter
from models.user import User
from models.activity import Activity

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@clients_bp.route("/")
@login_required
def index():
    clients = Client.query.order_by(Client.name).all()
    users = User.query.all()
    return render_template("clients.html", clients=clients, users=users)


@clients_bp.route("/add", methods=["POST"])
@login_required
def add():
    name = request.form.get("name")
    email = request.form.get("email", "")
    phone = request.form.get("phone", "")
    address = request.form.get("address", "")

    client = Client(name=name, email=email, phone=phone, address=address)
    db.session.add(client)
    db.session.commit()
    flash(f"Client '{name}' added successfully.", "success")
    return redirect(url_for("clients.index"))


@clients_bp.route("/<int:client_id>/add-matter", methods=["POST"])
@login_required
def add_matter(client_id):
    client = Client.query.get_or_404(client_id)
    title = request.form.get("title")
    description = request.form.get("description", "")
    count = Matter.query.count() + 1
    reference = f"MAT-2026-{count:03d}"

    matter = Matter(
        reference=reference, title=title, description=description,
        client_id=client.id, status="active",
    )
    matter.team.append(current_user)
    db.session.add(matter)
    db.session.commit()
    flash(f"Matter '{reference}' created for {client.name}.", "success")
    return redirect(url_for("clients.index"))

@clients_bp.route("/matter/<int:matter_id>/assign", methods=["POST"])
@login_required
def assign_team(matter_id):
    matter = Matter.query.get_or_404(matter_id)
    user_id = request.form.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user and user not in matter.team:
            matter.team.append(user)
            db.session.commit()
            flash(f"{user.name} assigned to matter {matter.reference}.", "success")
        elif user in matter.team:
            flash(f"{user.name} is already assigned to this matter.", "info")
    return redirect(url_for("clients.index"))

@clients_bp.route("/matter/<int:matter_id>/remove-team", methods=["POST"])
@login_required
def remove_team(matter_id):
    matter = Matter.query.get_or_404(matter_id)
    user_id = request.form.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user and user in matter.team:
            matter.team.remove(user)
            db.session.commit()
            flash(f"{user.name} removed from matter {matter.reference}.", "success")
    return redirect(url_for("clients.index"))

@clients_bp.route("/matter/<int:matter_id>")
@login_required
def matter_detail(matter_id):
    matter = Matter.query.get_or_404(matter_id)
    
    # Optional: Restrict access to team members or managers
    if current_user not in matter.team and current_user.role != 'manager':
        flash("You are not assigned to this matter.", "error")
        return redirect(url_for("clients.index"))
        
    activities = Activity.query.filter_by(matter_id=matter.id).order_by(Activity.started_at.desc()).all()
    
    return render_template("matter_detail.html", matter=matter, activities=activities)
