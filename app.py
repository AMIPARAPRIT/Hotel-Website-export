import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_proto=1, x_host=1
)  # needed for url_for to generate with https

# Use in-memory SQLite database for MVP
# Get the database URL, ensure it uses the correct PostgreSQL dialect
database_url = os.environ.get("DATABASE_URL", "sqlite:///hotel.db")
# If the DATABASE_URL starts with "postgres://", replace it with "postgresql://"
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
logging.info(
    f"Using database: {database_url.split('@')[0]}@..."
)  # Log without credentials
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models and routes
    import models  # noqa: F401
    import routes  # noqa: F401

    # Create database tables
    db.create_all()

    # Add initial admin user if none exists
    from models import User
    from werkzeug.security import generate_password_hash

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@hotel.com",
            password_hash=generate_password_hash("admin123"),
            is_admin=True,
        )
        db.session.add(admin)

        # Add some initial rooms
        from models import Room

        room_data = [
            {
                "name": "Standard Room",
                "description": "Comfortable room with essential amenities for a relaxing stay.",
                "image_url": "https://images.unsplash.com/photo-1566665797739-1674de7a421a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                "price": 99.99,
                "capacity": 2,
                "amenities": "Wi-Fi, TV, AC, Mini-bar",
            },
            {
                "name": "Deluxe Room",
                "description": "Spacious room with premium amenities and city view.",
                "image_url": "https://images.unsplash.com/photo-1590490360182-c33d57733427?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                "price": 149.99,
                "capacity": 2,
                "amenities": "Wi-Fi, TV, AC, Mini-bar, Room Service, City View",
            },
            {
                "name": "Suite",
                "description": "Luxury suite with separate living area and panoramic views.",
                "image_url": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80",
                "price": 249.99,
                "capacity": 4,
                "amenities": "Wi-Fi, Smart TV, AC, Mini-bar, Room Service, Panoramic View, Jacuzzi",
            },
        ]

        for data in room_data:
            room = Room(**data)
            db.session.add(room)

        db.session.commit()
        logging.info("Initial data added to the database")
