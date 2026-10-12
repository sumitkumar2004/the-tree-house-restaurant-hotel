from datetime import datetime, date
import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, g

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
DATABASE = os.path.join(app.root_path, "tree_house.db")

MENU = [
    {"id": "m1", "name": "Paneer Tikka", "category": "Starters", "price": 249, "description": "Smoky tandoori paneer with mint chutney.", "emoji": "🥘", "veg": True},
    {"id": "m2", "name": "Crispy Corn", "category": "Starters", "price": 189, "description": "Golden crispy corn tossed with herbs.", "emoji": "🌽", "veg": True},
    {"id": "m3", "name": "Butter Chicken", "category": "Main Course", "price": 349, "description": "Creamy tomato gravy with tender chicken.", "emoji": "🍛", "veg": False},
    {"id": "m4", "name": "Paneer Lababdar", "category": "Main Course", "price": 299, "description": "Paneer in a rich, aromatic curry.", "emoji": "🍲", "veg": True},
    {"id": "m5", "name": "Veg Biryani", "category": "Rice & Biryani", "price": 229, "description": "Fragrant basmati rice, vegetables and spices.", "emoji": "🍚", "veg": True},
    {"id": "m6", "name": "Chicken Biryani", "category": "Rice & Biryani", "price": 289, "description": "Aromatic dum biryani served with raita.", "emoji": "🍗", "veg": False},
    {"id": "m7", "name": "Masala Chai", "category": "Drinks", "price": 59, "description": "Freshly brewed Indian spiced tea.", "emoji": "☕", "veg": True},
    {"id": "m8", "name": "Chocolate Brownie", "category": "Desserts", "price": 149, "description": "Warm chocolate brownie for a sweet finish.", "emoji": "🍫", "veg": True},
]

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL, phone TEXT NOT NULL, address TEXT NOT NULL,
            items TEXT NOT NULL, total INTEGER NOT NULL, notes TEXT,
            created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Received'
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
            booking_type TEXT NOT NULL, checkin TEXT, checkout TEXT,
            guests INTEGER NOT NULL, room_type TEXT, special_requests TEXT,
            created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'Pending'
        )""")

@app.route("/")
def index():
    categories = list(dict.fromkeys(item["category"] for item in MENU))
    return render_template("index.html", menu=MENU, categories=categories)

@app.route("/order", methods=["POST"])
def order():
    name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    notes = request.form.get("notes", "").strip()
    if not name or not phone or not address:
        flash("Please fill in your name, phone number and delivery address.", "error")
        return redirect(url_for("index") + "#menu")

    quantities = {}
    total = 0
    summary = []
    for item in MENU:
        try:
            qty = max(0, min(50, int(request.form.get(f"qty_{item['id']}", "0"))))
        except ValueError:
            qty = 0
        if qty:
            quantities[item["id"]] = qty
            total += item["price"] * qty
            summary.append(f"{item['name']} x {qty} (₹{item['price'] * qty})")
    if not summary:
        flash("Please choose at least one menu item before placing an order.", "error")
        return redirect(url_for("index") + "#menu")

    db = get_db()
    cur = db.execute(
        "INSERT INTO orders (customer_name, phone, address, items, total, notes, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, phone, address, "; ".join(summary), total, notes, datetime.now().isoformat(timespec="minutes"))
    )
    db.commit()
    return render_template("confirmation.html", kind="order", reference=cur.lastrowid, name=name, total=total, details=summary)

@app.route("/booking", methods=["POST"])
def booking():
    name = request.form.get("guest_name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    booking_type = request.form.get("booking_type", "room")
    checkin = request.form.get("checkin", "")
    checkout = request.form.get("checkout", "")
    guests_raw = request.form.get("guests", "1")
    room_type = request.form.get("room_type", "Deluxe Room")
    special = request.form.get("special_requests", "").strip()
    try:
        guests = max(1, min(20, int(guests_raw)))
    except ValueError:
        guests = 1

    if not name or not email or not phone:
        flash("Please fill in your name, email and phone number.", "error")
        return redirect(url_for("index") + "#booking")
    if booking_type == "room":
        if not checkin or not checkout or checkout <= checkin:
            flash("For a room booking, choose a valid check-in and check-out date.", "error")
            return redirect(url_for("index") + "#booking")
        if checkin < date.today().isoformat():
            flash("Check-in date cannot be in the past.", "error")
            return redirect(url_for("index") + "#booking")
    else:
        checkin = checkin or None
        checkout = checkout or None

    db = get_db()
    cur = db.execute(
        """INSERT INTO bookings (guest_name, email, phone, booking_type, checkin, checkout, guests, room_type, special_requests, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (name, email, phone, booking_type, checkin, checkout, guests, room_type if booking_type == "room" else None,
         special, datetime.now().isoformat(timespec="minutes"))
    )
    db.commit()
    return render_template("confirmation.html", kind="booking", reference=cur.lastrowid, name=name, total=None,
                           details=[f"Type: {'Hotel room' if booking_type == 'room' else 'Restaurant table'}",
                                    f"Guests: {guests}",
                                    f"Dates: {checkin or 'Not specified'} to {checkout or 'Not specified'}",
                                    f"Room: {room_type if booking_type == 'room' else 'Not applicable'}"])

@app.route("/admin", methods=["GET"])
def admin():
    # Demo admin view. Add authentication before deploying publicly.
    orders = get_db().execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
    bookings = get_db().execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 100").fetchall()
    return render_template("admin.html", orders=orders, bookings=bookings)

@app.route("/health")
def health():
    return {"status": "ok"}

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
