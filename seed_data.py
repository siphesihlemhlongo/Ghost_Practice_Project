"""Seed the database with demo data for presentation."""
import random
from datetime import datetime, timedelta
from app import create_app
from models import db
from models.user import User
from models.client import Client
from models.matter import Matter
from models.activity import Activity
from models.time_entry import TimeEntry

app = create_app()

CLIENTS_DATA = [
    {"name": "Vodacom Group Ltd", "email": "legal@vodacom.co.za", "phone": "+27 11 653 5000", "address": "082 Vodacom Blvd, Midrand"},
    {"name": "Sasol Limited", "email": "contracts@sasol.com", "phone": "+27 10 344 5000", "address": "50 Katherine St, Sandton"},
    {"name": "Woolworths Holdings", "email": "legal@woolworths.co.za", "phone": "+27 21 407 9111", "address": "93 Longmarket St, Cape Town"},
    {"name": "Discovery Ltd", "email": "compliance@discovery.co.za", "phone": "+27 11 529 2888", "address": "1 Discovery Pl, Sandton"},
    {"name": "Nkosi Property Group", "email": "info@nkosiprop.co.za", "phone": "+27 11 880 3200", "address": "22 Houghton Dr, Houghton Estate"},
]

MATTERS_DATA = [
    {"client_idx": 0, "title": "Spectrum Licensing Agreement", "desc": "Telecommunications spectrum licensing and regulatory compliance"},
    {"client_idx": 0, "title": "Employment Dispute - Dept Head", "desc": "Unfair dismissal claim by former department head"},
    {"client_idx": 1, "title": "Environmental Compliance Review", "desc": "Annual environmental regulatory compliance review"},
    {"client_idx": 1, "title": "Joint Venture Agreement - Mozambique", "desc": "Cross-border joint venture for gas exploration"},
    {"client_idx": 2, "title": "Lease Negotiation - Mall of Africa", "desc": "Commercial lease agreement for new retail space"},
    {"client_idx": 3, "title": "Medical Scheme Regulatory Filing", "desc": "Council for Medical Schemes annual compliance filing"},
    {"client_idx": 3, "title": "Data Protection Impact Assessment", "desc": "POPIA compliance assessment for new digital platform"},
    {"client_idx": 4, "title": "Property Acquisition - Rosebank", "desc": "Commercial property purchase and transfer"},
    {"client_idx": 4, "title": "Tenant Eviction Proceedings", "desc": "Rental arrears and eviction proceedings"},
]

ACTIVITY_TEMPLATES = [
    ("email", "Reviewed and responded to client correspondence", (5, 25)),
    ("email", "Drafted response to opposing counsel", (10, 35)),
    ("email", "Sent progress update to client", (5, 15)),
    ("meeting", "Client consultation meeting", (30, 90)),
    ("meeting", "Internal strategy discussion", (20, 60)),
    ("call", "Phone consultation with client", (5, 30)),
    ("call", "Conference call with counsel", (15, 45)),
    ("document", "Drafted contract amendments", (30, 120)),
    ("document", "Reviewed agreement and provided comments", (20, 90)),
    ("document", "Prepared court submissions", (45, 180)),
    ("research", "Legal research - applicable case law", (30, 120)),
    ("research", "Statutory and regulatory research", (20, 60)),
]


def seed():
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()

        # Create users
        attorney = User(name="Sphesihle Mkhize", email="sphesihle@mb.co.za", role="attorney", hourly_rate=2500.00)
        attorney.set_password("password123")

        manager = User(name="Thabo Ndlovu", email="thabo@mb.co.za", role="manager", hourly_rate=3200.00)
        manager.set_password("password123")

        associate = User(name="Naledi Mokoena", email="naledi@mb.co.za", role="attorney", hourly_rate=1800.00)
        associate.set_password("password123")

        attorney2 = User(name="Sarah Connor", email="sarah@mb.co.za", role="attorney", hourly_rate=2200.00)
        attorney2.set_password("password123")

        paralegal = User(name="David Miller", email="david@mb.co.za", role="attorney", hourly_rate=1200.00)
        paralegal.set_password("password123")

        manager2 = User(name="John Smith", email="john@mb.co.za", role="manager", hourly_rate=3500.00)
        manager2.set_password("password123")

        db.session.add_all([attorney, manager, associate, attorney2, paralegal, manager2])
        db.session.flush()

        # Create clients
        clients = []
        for c in CLIENTS_DATA:
            client = Client(**c)
            db.session.add(client)
            clients.append(client)
        db.session.flush()

        # Create matters
        all_users = [attorney, manager, associate, attorney2, paralegal, manager2]
        matters = []
        for i, m in enumerate(MATTERS_DATA):
            matter = Matter(
                reference=f"MAT-2026-{i+1:03d}",
                title=m["title"],
                description=m["desc"],
                client_id=clients[m["client_idx"]].id,
                status="active",
            )
            
            # Assign random team members
            team_size = random.randint(1, 3)
            matter.team = random.sample(all_users, team_size)
            
            db.session.add(matter)
            matters.append(matter)
        db.session.flush()

        # Create activities and time entries for the past 7 days
        today = datetime.utcnow().date()
        sources = ["outlook", "teams", "auto-detect", "manual"]

        for day_offset in range(7):
            d = today - timedelta(days=day_offset)
            num_activities = random.randint(4, 8)

            for _ in range(num_activities):
                tmpl = random.choice(ACTIVITY_TEMPLATES)
                matter = random.choice(matters)
                assigned_user = random.choice(matter.team)
                dur = random.randint(tmpl[2][0], tmpl[2][1])
                hour = random.randint(8, 17)
                started = datetime.combine(d, datetime.min.time().replace(hour=hour))
                ended = started + timedelta(minutes=dur)

                activity = Activity(
                    user_id=assigned_user.id,
                    type=tmpl[0],
                    title=f"{tmpl[1]} - {matter.title}",
                    description=f"Work on {matter.reference}",
                    source=random.choice(sources),
                    started_at=started,
                    ended_at=ended,
                    duration_minutes=dur,
                    matter_id=matter.id,
                    status="pending" if day_offset == 0 or random.random() < 0.3 else "converted",
                )
                db.session.add(activity)
                db.session.flush()

                # Create time entries only for converted activities
                if activity.status == "converted":
                    entry = TimeEntry(
                        activity_id=activity.id,
                        user_id=assigned_user.id,
                        matter_id=matter.id,
                        date=d,
                        start_time=started.time(),
                        end_time=ended.time(),
                        description=f"{tmpl[0].title()}: {tmpl[1]} - {matter.title}",
                        duration_minutes=dur,
                        rate=attorney.hourly_rate,
                        units=0, amount=0,
                        status="approved" if day_offset > 2 else "draft",
                    )
                    entry.compute_billing()
                    db.session.add(entry)

        # GUARANTEE OVERDUES FOR SPHESIHLE
        four_days_ago = today - timedelta(days=4)
        for i in range(3):
            matter = matters[i]
            dur = 25 + (i * 10)
            started = datetime.combine(four_days_ago, datetime.min.time().replace(hour=10 + i))
            activity = Activity(
                user_id=attorney.id,
                type="email",
                title=f"Review opposing counsel email - {matter.title}",
                description="Long email thread review",
                source="outlook",
                started_at=started,
                ended_at=started + timedelta(minutes=dur),
                duration_minutes=dur,
                matter_id=matter.id,
                status="pending"
            )
            db.session.add(activity)

        db.session.commit()
        print("Database seeded successfully!")
        print(f"Users: {User.query.count()}")
        print(f"Clients: {Client.query.count()}")
        print(f"Matters: {Matter.query.count()}")
        print(f"Activities: {Activity.query.count()}")
        print(f"Time Entries: {TimeEntry.query.count()}")


if __name__ == "__main__":
    seed()
