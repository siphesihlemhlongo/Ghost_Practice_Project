from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db
from models.client import Client
from models.matter import Matter

clients_bp = Blueprint("clients", __name__, url_prefix="/clients")


@clients_bp.route("/")
@login_required
def index():
    clients = Client.query.order_by(Client.name).all()
    return render_template("clients.html", clients=clients)


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
    db.session.add(matter)
    db.session.commit()
    flash(f"Matter '{reference}' created for {client.name}.", "success")
    return redirect(url_for("clients.index"))
