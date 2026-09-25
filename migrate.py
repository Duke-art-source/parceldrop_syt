import os
from app import app, db

def init_db():
    """Initialize database tables"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database initialized successfully!")

if __name__ == "__main__":
    init_db()