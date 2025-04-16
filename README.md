# 🏨 Hotel Booking Web App (Flask + SQLite)

A simple hotel room booking website built using Flask, SQLAlchemy, and SQLite for the backend. Ideal for learning full-stack development and deploying MVPs.

---

## 🚀 Features

- Admin panel with initial admin account
- Room listing with images, amenities, and prices
- User registration and login
- Room booking system
- Session management using Flask-Login

---

## 🗂 Project Structure
HOTEL /
│
├── static/ # Static files (CSS, JS, images)
├── templates/ # HTML templates (Jinja2)
│ └── admin/ # Admin-specific templates
├── app.py # Main app configuration
├── main.py # Entry point (creates DB, seeds data)
├── models.py # Database models (User, Room, etc.)
├── routes.py # App routes and views
├── hotel.db # SQLite database (auto-created)
├── requirements.txt # Python dependencies
└── README.md # Project documentation

---

## 🧰 Requirements

Make sure Python 3.10+ is installed.

### 🧪 Install dependencies:
```bash
pip install Flask Flask-SQLAlchemy Flask-Login psycopg2-binary Werkzeug


pip install -r requirements.txt

