from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect

# Create the database instance
db = SQLAlchemy()

def create_app(config_overrides=None):
    app = Flask(__name__)

    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///pas.sqlite"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if config_overrides:
        app.config.update(config_overrides)

    # Initialize the database with the app
    db.init_app(app) # [1] Adapted with assistance from ChatGPT to correctly initialize SQLAlchemy with Flask context

    # Import model inside the function
    from .models.analysis import Analysis # [2] Adapted with assistance from ChatGPT to resolve circular import issues

    # Create table if it doesn't exist
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table('analyses'):
            db.create_all()
            print("Created 'analyses' table")  # [3] ChatGPT helped guide logic for checking table existence using SQLAlchemy inspector

    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/api/v1')  # [4] ChatGPT clarified blueprint registration and prefix usage

    return app

