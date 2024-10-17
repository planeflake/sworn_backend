from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Set your database URI in the configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:.@10.0.0.200/rpg'

    # Initialize the extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models after db is initialized
    with app.app_context():
        from .models import Skill, Stat, Character, CharacterResources, CharacterSkill, Task, CharacterTask, StartingArea

    # Import and register blueprints
    from .routes import admin_bp, task_bp, resource_bp
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(task_bp, url_prefix='/api')
    app.register_blueprint(resource_bp, url_prefix='/api/resources')

    return app