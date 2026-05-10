import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "ghost-practice-secret-key-2026")
    
    db_url = os.environ.get("DATABASE_URL")
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    SQLALCHEMY_DATABASE_URI = db_url or ("sqlite:///" + os.path.join(BASE_DIR, "instance", "ghost.db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Billing defaults
    DEFAULT_HOURLY_RATE = 2500.00  # R2,500 per hour
    BILLING_INCREMENT_MINUTES = 6  # 6-minute billing increments
    VAT_RATE = 0.15  # 15% VAT
