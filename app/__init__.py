from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    from .routes import admin_bp
    CORS(app)
    app.register_blueprint(admin_bp, url_prefix='/api')
    # Set your database URI in the configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:.@10.0.0.200/rpg'

    # Initialize the extensions
    db.init_app(app)
    migrate.init_app(app, db)

    from .models import Skill,Stat,Character,CharacterStat


    # Import and register your blueprints (if any)
    # Example: app.register_blueprint(some_blueprint)

    return app
