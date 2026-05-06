import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ghost-practice-secret-key-2026")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(BASE_DIR, "instance", "ghost.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Billing defaults
    DEFAULT_HOURLY_RATE = 2500.00  # R2,500 per hour
    BILLING_INCREMENT_MINUTES = 6  # 6-minute billing increments
    VAT_RATE = 0.15  # 15% VAT
