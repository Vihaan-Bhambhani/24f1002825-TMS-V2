from flask import Flask
from config import Config
from extensions import db
from models import User, StaffProfile, Trek, Booking
from seed import seed_admin


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Create database tables and seed admin
    with app.app_context():
        db.create_all()
        seed_admin()

    # Health check route
    @app.route('/')
    def index():
        return {'message': 'TMS V2 API is running'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
