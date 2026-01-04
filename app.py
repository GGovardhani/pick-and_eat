import os
import sqlite3
from flask import Flask, flash, session, redirect, url_for, request, render_template, g
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from logging.handlers import RotatingFileHandler

# ------------------------------
# Flask App Setup
# ------------------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

# ------------------------------
# Logger Setup
# ------------------------------
file_handler = RotatingFileHandler("app.log", maxBytes=100000, backupCount=3)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app.logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
app.logger.addHandler(console_handler)

# ------------------------------
# Database Setup
# ------------------------------
DATABASE = "users.db"

def get_db():
    """Connect to SQLite database and store connection in Flask's g"""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close DB connection on app context teardown"""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def init_db():
    """Create users table if not exists"""
    with app.app_context():
        db = get_db()
        db.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )"""
        )
        db.commit()
        app.logger.info("Database initialized")

# ------------------------------
# Routes
# ------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("All fields are required")
            return redirect(url_for("register"))

        if len(username) < 3:
            flash("Username must have at least 3 characters")
            return redirect(url_for("register"))

        db = get_db()
        cursor = db.cursor()

        # Check if user exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            flash("User already exists")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        db.commit()

        flash("Registration successful, please login")
        app.logger.info(f"New user registered: {username}")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user is None:
            flash("User not found")
            app.logger.warning(f"Failed login attempt for: {username}")
            return redirect(url_for("login"))

        if not check_password_hash(user["password"], password):
            flash("Wrong password")
            app.logger.warning(f"Wrong password attempt for: {username}")
            return redirect(url_for("login"))

        session["user"] = username
        flash("Login successful")
        app.logger.info(f"User logged in: {username}")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please login first")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    username = session.get("user")
    session.pop("user", None)
    flash("Logged out successfully")
    app.logger.info(f"User logged out: {username}")
    return redirect(url_for("login"))

@app.route("/pandu")
def pandu():
    flash("Hey there!")
    return render_template("pandu.html")

# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    init_db()  # Ensure DB is ready
    app.run(debug=True)
