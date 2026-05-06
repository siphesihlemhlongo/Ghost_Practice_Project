from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.activities import activities_bp
from routes.time_entries import time_entries_bp
from routes.invoices import invoices_bp
from routes.clients import clients_bp
from routes.api import api_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(time_entries_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(api_bp)
