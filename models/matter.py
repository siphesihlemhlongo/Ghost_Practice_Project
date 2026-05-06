from models import db
from datetime import datetime


class Matter(db.Model):
    __tablename__ = "matters"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    status = db.Column(db.String(20), default="active")  # active / closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    activities = db.relationship("Activity", backref="matter", lazy="dynamic")
    time_entries = db.relationship("TimeEntry", backref="matter", lazy="dynamic")
    invoices = db.relationship("Invoice", backref="matter", lazy="dynamic")

    def __repr__(self):
        return f"<Matter {self.reference}: {self.title}>"
