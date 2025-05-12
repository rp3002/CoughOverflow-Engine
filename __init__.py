from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
import os  # To read DATABASE_URL from environment variables

# Create the database instance
db = SQLAlchemy()

def create_app(config_overrides=None):
    app = Flask(__name__)

    # Use DATABASE_URL from environment for PostgreSQL, fallback to local SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        "DATABASE_URL", "sqlite:///pas.sqlite"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_overrides:
        app.config.update(config_overrides)

    # Initialize the database with the app
    db.init_app(app)

    # Import model inside the function
    from .models.analysis import Analysis

    # Create table if it doesn't exist (for both SQLite and PostgreSQL)
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('analyses'):
            db.create_all()
            print("Created 'analyses' table in", db.engine.url.drivername)
        else:
            print("'analyses' table already exists in", db.engine.url.drivername)

    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/api/v1')

    return app
