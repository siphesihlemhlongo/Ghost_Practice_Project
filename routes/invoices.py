from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db
from models.invoice import Invoice, InvoiceItem
from models.time_entry import TimeEntry
from models.matter import Matter
from models.client import Client
from datetime import datetime

invoices_bp = Blueprint("invoices", __name__, url_prefix="/invoices")


@invoices_bp.route("/")
@login_required
def index():
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    matters = Matter.query.filter_by(status="active").all()
    return render_template("invoices.html", invoices=invoices, matters=matters)


@invoices_bp.route("/generate", methods=["POST"])
@login_required
def generate():
    matter_id = request.form.get("matter_id")
    if not matter_id:
        flash("Please select a matter.", "error")
        return redirect(url_for("invoices.index"))

    matter = Matter.query.get_or_404(int(matter_id))

    # Get approved, unbilled time entries for this matter
    entries = TimeEntry.query.filter_by(
        matter_id=matter.id, status="approved"
    ).all()

    if not entries:
        flash("No approved time entries found for this matter.", "error")
        return redirect(url_for("invoices.index"))

    # Create invoice
    invoice = Invoice(
        invoice_number=Invoice.generate_invoice_number(),
        matter_id=matter.id,
        client_id=matter.client_id,
        date_issued=datetime.utcnow().date(),
        status="draft",
        notes=f"Professional fees in respect of {matter.title}",
    )
    invoice.set_due_date()
    db.session.add(invoice)
    db.session.flush()  # Get invoice ID

    # Create invoice items from time entries
    for entry in entries:
        desc = entry.description
        if entry.date:
            date_str = entry.date.strftime('%d %b %Y')
            time_str = ""
            if entry.start_time and entry.end_time:
                time_str = f" ({entry.start_time.strftime('%H:%M')} - {entry.end_time.strftime('%H:%M')})"
            desc = f"{date_str}{time_str} - {desc}"

        item = InvoiceItem(
            invoice_id=invoice.id,
            time_entry_id=entry.id,
            description=desc,
            units=entry.units,
            rate=entry.rate,
            amount=entry.amount,
        )
        db.session.add(item)
        entry.status = "billed"

    db.session.flush()
    invoice.calculate_totals()
    db.session.commit()

    flash(f"Invoice {invoice.invoice_number} generated (R{invoice.total:,.2f}).", "success")
    return redirect(url_for("invoices.detail", invoice_id=invoice.id))


@invoices_bp.route("/<int:invoice_id>")
@login_required
def detail(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    items = invoice.items.all()
    return render_template("invoice_detail.html", invoice=invoice, items=items)


@invoices_bp.route("/<int:invoice_id>/pdf")
@login_required
def pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    items = invoice.items.all()
    return render_template("invoice_pdf.html", invoice=invoice, items=items)


@invoices_bp.route("/<int:invoice_id>/send", methods=["POST"])
@login_required
def send_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.status = "sent"
    db.session.commit()
    flash(f"Invoice {invoice.invoice_number} marked as sent.", "success")
    return redirect(url_for("invoices.detail", invoice_id=invoice.id))


@invoices_bp.route("/<int:invoice_id>/paid", methods=["POST"])
@login_required
def mark_paid(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice.status = "paid"
    db.session.commit()
    flash(f"Invoice {invoice.invoice_number} marked as paid.", "success")
    return redirect(url_for("invoices.detail", invoice_id=invoice.id))
