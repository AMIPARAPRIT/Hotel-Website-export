import logging
from datetime import datetime
from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session,
    g,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from functools import wraps
from app import app, db
from models import User, Room, Booking

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You need admin privileges to access this page.", "danger")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


# Public routes
@app.route("/")
def index():
    featured_rooms = Room.query.limit(3).all()
    return render_template("index.html", featured_rooms=featured_rooms)


@app.route("/rooms")
def rooms():
    rooms = Room.query.all()
    return render_template("rooms.html", rooms=rooms)


@app.route("/rooms/<int:room_id>")
def room_detail(room_id):
    room = Room.query.get_or_404(room_id)
    return render_template("room_detail.html", room=room)


@app.route("/booking/<int:room_id>", methods=["GET", "POST"])
def booking(room_id):
    room = Room.query.get_or_404(room_id)

    if request.method == "POST":
        # Get form data
        guest_name = request.form.get("guest_name")
        guest_email = request.form.get("guest_email")
        guest_phone = request.form.get("guest_phone")
        check_in_date = datetime.strptime(
            request.form.get("check_in_date"), "%Y-%m-%d"
        ).date()
        check_out_date = datetime.strptime(
            request.form.get("check_out_date"), "%Y-%m-%d"
        ).date()
        num_guests = int(request.form.get("num_guests"))

        # Handle user authentication
        if current_user.is_authenticated:
            user_id = current_user.id

            # If user is logged in, use their email if not provided
            if not guest_email:
                guest_email = current_user.email

        else:
            # Encourage registration instead of creating a temporary user
            flash("Please login or register to complete your booking.", "warning")
            session["booking_data"] = {
                "room_id": room_id,
                "guest_name": guest_name,
                "guest_email": guest_email,
                "guest_phone": guest_phone,
                "check_in_date": request.form.get("check_in_date"),
                "check_out_date": request.form.get("check_out_date"),
                "num_guests": num_guests,
            }
            return redirect(url_for("login"))

        # Create booking
        booking = Booking(
            user_id=user_id,
            room_id=room_id,
            guest_name=guest_name,
            guest_email=guest_email,
            guest_phone=guest_phone,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            num_guests=num_guests,
            status="pending",
        )

        db.session.add(booking)
        db.session.commit()

        flash("Your booking has been submitted and is pending confirmation.", "success")

        # Redirect to user bookings page if user is logged in
        if current_user.is_authenticated:
            return redirect(url_for("user_bookings"))
        return redirect(url_for("index"))

    return render_template("booking.html", room=room)


# Authentication routes
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Validate form data
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for("register"))

        if User.query.filter_by(email=email).first():
            flash("Email already exists", "danger")
            return redirect(url_for("register"))

        # Create new user
        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            is_admin=False,
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")

            # Check if there's pending booking data in session
            if "booking_data" in session:
                booking_data = session.pop("booking_data")
                room_id = booking_data.get("room_id")

                # Create booking from saved data
                booking = Booking(
                    user_id=user.id,
                    room_id=room_id,
                    guest_name=booking_data.get("guest_name"),
                    guest_email=booking_data.get("guest_email") or user.email,
                    guest_phone=booking_data.get("guest_phone"),
                    check_in_date=datetime.strptime(
                        booking_data.get("check_in_date"), "%Y-%m-%d"
                    ).date(),
                    check_out_date=datetime.strptime(
                        booking_data.get("check_out_date"), "%Y-%m-%d"
                    ).date(),
                    num_guests=booking_data.get("num_guests"),
                    status="pending",
                )

                db.session.add(booking)
                db.session.commit()

                flash(
                    "Your booking has been submitted and is pending confirmation.",
                    "success",
                )
                return redirect(url_for("user_bookings"))

            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            return redirect(url_for("index"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))


@app.route("/my-bookings")
@login_required
def user_bookings():
    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return render_template("user_bookings.html", bookings=bookings)


@app.route("/bookings/<int:booking_id>/cancel", methods=["POST"])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if booking belongs to current user
    if booking.user_id != current_user.id:
        flash("You do not have permission to cancel this booking", "danger")
        return redirect(url_for("user_bookings"))

    # Check if booking is pending
    if booking.status != "pending":
        flash("This booking cannot be cancelled", "warning")
        return redirect(url_for("user_bookings"))

    booking.status = "cancelled"
    db.session.commit()

    flash("Booking cancelled successfully", "success")
    return redirect(url_for("user_bookings"))


# Admin routes
@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    rooms_count = Room.query.count()
    bookings_count = Booking.query.count()
    pending_bookings = Booking.query.filter_by(status="pending").count()

    # Get recent bookings for dashboard
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()

    # Get booking statistics for chart
    booking_stats = {
        "labels": ["Pending", "Confirmed", "Cancelled"],
        "data": [
            Booking.query.filter_by(status="pending").count(),
            Booking.query.filter_by(status="confirmed").count(),
            Booking.query.filter_by(status="cancelled").count(),
        ],
    }

    return render_template(
        "admin/dashboard.html",
        rooms_count=rooms_count,
        bookings_count=bookings_count,
        pending_bookings=pending_bookings,
        recent_bookings=recent_bookings,
        booking_stats=booking_stats,
    )


@app.route("/admin/rooms")
@login_required
@admin_required
def admin_rooms():
    rooms = Room.query.all()
    return render_template("admin/rooms.html", rooms=rooms)


@app.route("/admin/rooms/add", methods=["POST"])
@login_required
@admin_required
def add_room():
    name = request.form.get("name")
    description = request.form.get("description")
    image_url = request.form.get("image_url")
    price = float(request.form.get("price"))
    capacity = int(request.form.get("capacity"))
    amenities = request.form.get("amenities")

    room = Room(
        name=name,
        description=description,
        image_url=image_url,
        price=price,
        capacity=capacity,
        amenities=amenities,
        is_available=True,
    )

    db.session.add(room)
    db.session.commit()

    flash("Room added successfully", "success")
    return redirect(url_for("admin_rooms"))


@app.route("/admin/rooms/<int:room_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)

    room.name = request.form.get("name")
    room.description = request.form.get("description")
    room.image_url = request.form.get("image_url")
    room.price = float(request.form.get("price"))
    room.capacity = int(request.form.get("capacity"))
    room.amenities = request.form.get("amenities")
    room.is_available = "is_available" in request.form

    db.session.commit()

    flash("Room updated successfully", "success")
    return redirect(url_for("admin_rooms"))


@app.route("/admin/rooms/<int:room_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)

    # Check if room has bookings
    if room.bookings.count() > 0:
        flash("Cannot delete room with bookings", "danger")
        return redirect(url_for("admin_rooms"))

    db.session.delete(room)
    db.session.commit()

    flash("Room deleted successfully", "success")
    return redirect(url_for("admin_rooms"))


@app.route("/admin/bookings")
@login_required
@admin_required
def admin_bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


@app.route("/admin/bookings/<int:booking_id>/status", methods=["POST"])
@login_required
@admin_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    status = request.form.get("status")

    if status in ["pending", "confirmed", "cancelled"]:
        booking.status = status
        db.session.commit()
        flash(f"Booking status updated to {status}", "success")
    else:
        flash("Invalid status", "danger")

    return redirect(url_for("admin_bookings"))


# API routes
@app.route("/api/rooms")
def api_rooms():
    rooms = Room.query.all()
    return jsonify([room.to_dict() for room in rooms])


@app.route("/api/rooms/<int:room_id>")
def api_room(room_id):
    room = Room.query.get_or_404(room_id)
    return jsonify(room.to_dict())


@app.route("/api/check_availability", methods=["POST"])
def check_availability():
    room_id = request.json.get("room_id")
    check_in = datetime.strptime(request.json.get("check_in"), "%Y-%m-%d").date()
    check_out = datetime.strptime(request.json.get("check_out"), "%Y-%m-%d").date()

    # Check for overlapping bookings
    overlapping_bookings = Booking.query.filter(
        Booking.room_id == room_id,
        Booking.status != "cancelled",
        Booking.check_in_date <= check_out,
        Booking.check_out_date >= check_in,
    ).count()

    return jsonify({"available": overlapping_bookings == 0})
