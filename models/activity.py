from models import db
from datetime import datetime


class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(30), nullable=False)  # email / meeting / call / document / research
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    source = db.Column(db.String(30), default="manual")  # outlook / teams / manual / auto-detect
    started_at = db.Column(db.DateTime, nullable=False)
    ended_at = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Float, default=0)
    matter_id = db.Column(db.Integer, db.ForeignKey("matters.id"), nullable=True)
    status = db.Column(db.String(20), default="pending")  # pending / converted / dismissed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    time_entry = db.relationship("TimeEntry", backref="activity", uselist=False)

    def calculate_duration(self):
        """Calculate duration in minutes from start and end times."""
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            self.duration_minutes = round(delta.total_seconds() / 60, 2)
        return self.duration_minutes

    @property
    def type_icon(self):
        """Return Font Awesome icon class for activity type."""
        icons = {
            "email": "fa-envelope",
            "meeting": "fa-users",
            "call": "fa-phone",
            "document": "fa-file-alt",
            "research": "fa-search",
        }
        return icons.get(self.type, "fa-clock")

    def __repr__(self):
        return f"<Activity {self.type}: {self.title}>"
