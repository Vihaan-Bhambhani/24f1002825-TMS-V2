from flask import Flask
from config import Config
from extensions import db


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Create database tables
    with app.app_context():
        db.create_all()

    # Health check route
    @app.route('/')
    def index():
        return {'message': 'TMS V2 API is running'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
