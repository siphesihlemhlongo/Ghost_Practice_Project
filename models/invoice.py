from models import db
from datetime import datetime, timedelta


class Invoice(db.Model):
    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    matter_id = db.Column(db.Integer, db.ForeignKey("matters.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    date_issued = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    subtotal = db.Column(db.Float, default=0)
    vat = db.Column(db.Float, default=0)
    total = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="draft")  # draft / sent / paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # Relationships
    items = db.relationship("InvoiceItem", backref="invoice", lazy="dynamic", cascade="all, delete-orphan")
    client = db.relationship("Client", backref="invoices")

    def calculate_totals(self, vat_rate=0.15):
        """Calculate subtotal, VAT, and total from invoice items."""
        self.subtotal = sum(item.amount for item in self.items)
        self.vat = round(self.subtotal * vat_rate, 2)
        self.total = round(self.subtotal + self.vat, 2)

    def set_due_date(self, days=30):
        """Set due date to N days from issue date."""
        if self.date_issued:
            self.due_date = self.date_issued + timedelta(days=days)

    @staticmethod
    def generate_invoice_number():
        """Generate next invoice number."""
        last = Invoice.query.order_by(Invoice.id.desc()).first()
        if last:
            num = int(last.invoice_number.split("-")[-1]) + 1
        else:
            num = 1
        return f"INV-2026-{num:04d}"

    def __repr__(self):
        return f"<Invoice {self.invoice_number}: R{self.total}>"


class InvoiceItem(db.Model):
    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    time_entry_id = db.Column(db.Integer, db.ForeignKey("time_entries.id"), nullable=True)
    description = db.Column(db.Text, nullable=False)
    units = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)

    # Relationships
    time_entry = db.relationship("TimeEntry", backref="invoice_item")

    def __repr__(self):
        return f"<InvoiceItem {self.description[:30]}: R{self.amount}>"
