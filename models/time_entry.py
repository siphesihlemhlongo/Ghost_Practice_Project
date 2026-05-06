import math
from models import db
from datetime import datetime


class TimeEntry(db.Model):
    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey("activities.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    matter_id = db.Column(db.Integer, db.ForeignKey("matters.id"), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    start_time = db.Column(db.Time, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    description = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Float, nullable=False)
    units = db.Column(db.Float, nullable=False)  # duration / 6
    rate = db.Column(db.Float, nullable=False)  # R per hour
    amount = db.Column(db.Float, nullable=False)  # calculated
    status = db.Column(db.String(20), default="draft")  # draft / approved / billed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def round_to_units(minutes, increment=6):
        """Round minutes UP to nearest billing increment and return units."""
        return math.ceil(minutes / increment)

    @staticmethod
    def calculate_amount(units, hourly_rate, increment=6):
        """Calculate billing amount from units and hourly rate."""
        hours = (units * increment) / 60
        return round(hours * hourly_rate, 2)

    def compute_billing(self, increment=6):
        """Compute units and amount from duration and rate."""
        self.units = self.round_to_units(self.duration_minutes, increment)
        self.amount = self.calculate_amount(self.units, self.rate, increment)

    def __repr__(self):
        return f"<TimeEntry {self.id}: {self.units} units @ R{self.rate}/hr>"
