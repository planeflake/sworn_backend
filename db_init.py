from app import create_app, db

app = create_app()

with app.app_context():
    db.Model.metadata.clear()
    db.Model.metadata.create_all(db.engine)
    print("Database tables created successfully.")