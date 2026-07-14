from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
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
    CORS(app, origins=['http://localhost:5173'], supports_credentials=True)
    JWTManager(app)

    # Create database tables and seed admin
    with app.app_context():
        db.create_all()
        seed_admin()

    # Register blueprints
    from routes.auth import auth
    from routes.admin import admin
    from routes.staff import staff
    from routes.user import user
    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(staff)
    app.register_blueprint(user)

    # Health check route
    @app.route('/')
    def index():
        return {'message': 'TMS V2 API is running'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5001)
