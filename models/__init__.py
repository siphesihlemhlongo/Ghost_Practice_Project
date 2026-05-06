from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import User
from models.client import Client
from models.matter import Matter
from models.activity import Activity
from models.time_entry import TimeEntry
from models.invoice import Invoice, InvoiceItem
