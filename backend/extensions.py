from flask_sqlalchemy import SQLAlchemy

# Separate file to avoid circular imports
# Both app.py and models.py can import from here
db = SQLAlchemy()
