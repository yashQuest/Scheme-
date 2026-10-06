import os
import re
from functools import wraps
from flask import (
    Flask, render_template, request, url_for, flash, redirect,
    session, g, abort
)
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# Local business logic modules
from eligibility_engine import find_matching_schemes
from ai_extractor import extract_user_profile
from translator import SUPPORTED_LANGUAGES, get_language_name

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "OurScheme_Secret_Key_2026_Secure")

@app.context_processor
def inject_language_context():
    """Injects active language and supported languages dictionary into all Jinja templates."""
    return {
        "current_language": session.get("lang", "en"),
        "supported_languages": SUPPORTED_LANGUAGES,
        "get_language_name": get_language_name
    }

# Database configuration
DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "yash2622007"),
    "database": os.getenv("MYSQL_DATABASE", "government_schemes")
}


def get_db():
    """Returns a thread-safe database connection for the current Flask request context."""
    if "db" not in g or not g.db.is_connected():
        g.db = mysql.connector.connect(**DB_CONFIG)
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    """Closes the database connection at the end of the request."""
    db = g.pop("db", None)
    if db is not None and db.is_connected():
        db.close()


def get_user_saved_ids(user_id):
    """Returns a set of scheme IDs saved by the current user."""
    if not user_id:
        return set()
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT scheme_id FROM saved_schemes WHERE user_id = %s", (user_id,))
        return {row["scheme_id"] for row in cursor.fetchall()}
    except Exception:
        return set()


def admin_login_required(f):
    """Decorator to protect admin routes and enforce authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login to access the admin dashboard.", "warning")
            return redirect(url_for("admin_login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/set_language/<lang_code>", methods=["POST", "GET"])
def set_language(lang_code):
    """Sets active language in Flask session."""
    if lang_code in SUPPORTED_LANGUAGES:
        session["lang"] = lang_code
    return {"status": "success", "language": session.get("lang", "en")}


# ==================================================
# PUBLIC & SCHEME BROWSING ROUTES (UNCHANGED)
# ==================================================

@app.route("/")
@app.route("/home")
def home():
    """Renders the OurScheme homepage with scheme categories."""
    return render_template("home.html")


@app.route("/schemes")
def all_schemes():
    """Displays all available government schemes."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT s.*, c.category 
        FROM schemes s 
        LEFT JOIN categories c ON s.category_id = c.id 
        ORDER BY s.id ASC
    """
    cursor.execute(query)
    schemes = cursor.fetchall()
    saved_ids = get_user_saved_ids(session.get("user_id"))

    return render_template(
        "test.html",
        schemes=schemes,
        heading="All Government Schemes",
        sub_heading=f"Showing all {len(schemes)} welfare schemes and programs across India.",
        saved_ids=saved_ids
    )


@app.route("/find/<int:scheme_id>")
@app.route("/category/<int:scheme_id>")
def find(scheme_id):
    """Displays schemes belonging to a specific category."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT category FROM categories WHERE id = %s", (scheme_id,))
    cat_row = cursor.fetchone()
    category_name = cat_row["category"] if cat_row else "Schemes"

    query = """
        SELECT s.*, c.category 
        FROM schemes s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.category_id = %s
        ORDER BY s.id ASC
    """
    cursor.execute(query, (scheme_id,))
    schemes = cursor.fetchall()
    saved_ids = get_user_saved_ids(session.get("user_id"))

    return render_template(
        "test.html",
        schemes=schemes,
        heading=f"{category_name} Schemes",
        sub_heading=f"Found {len(schemes)} scheme(s) under {category_name}.",
        saved_ids=saved_ids
    )


@app.route("/search")
def search():
    """Searches schemes by scheme name, description, and category."""
    q = request.args.get("q", "").strip()
    if not q:
        return redirect(url_for("all_schemes"))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    pattern = f"%{q}%"
    query = """
        SELECT s.*, c.category 
        FROM schemes s 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE s.scheme_name LIKE %s 
           OR s.description LIKE %s 
           OR c.category LIKE %s
        ORDER BY s.id ASC
    """
    cursor.execute(query, (pattern, pattern, pattern))
    schemes = cursor.fetchall()
    saved_ids = get_user_saved_ids(session.get("user_id"))

    return render_template(
        "test.html",
        schemes=schemes,
        heading=f'Search Results for "{q}"',
        sub_heading=f"Found {len(schemes)} scheme(s) matching your search query.",
        saved_ids=saved_ids
    )


# ==================================================
# ELIGIBILITY & RECOMMENDATION ENGINE ROUTES
# ==================================================

@app.route("/Eligibility")
def eligibility():
    """Renders the step-by-step eligibility form page."""
    return render_template("eligibility.html")


@app.route("/check_eligibility", methods=["POST", "GET"])
def check_eligibility():
    """
    Receives submitted step-by-step eligibility form data,
    validates parameters, queries scheme database, and executes the
    deterministic Python recommendation engine.
    """
    if request.method == "GET":
        return redirect(url_for("eligibility"))

    raw_data = {
        "age": request.form.get("age", "").strip(),
        "gender": request.form.get("gender", "").strip(),
        "state": request.form.get("state", "").strip(),
        "district": request.form.get("district", "").strip(),
        "category": request.form.get("category", "").strip(),
        "income": request.form.get("income", "").strip(),
        "disability": request.form.get("disability", "No").strip(),
        "education": request.form.get("education", "").strip(),
        "occupation": request.form.get("occupation", "").strip(),
        "farmer": request.form.get("farmer", "No").strip(),
        "area_type": request.form.get("area_type", "All").strip(),
        "house_owner": request.form.get("house_owner", "No").strip(),
        "business_interest": request.form.get("business_interest", "No").strip(),
        "employment_seeking": request.form.get("employment_seeking", "No").strip()
    }

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, c.category 
        FROM schemes s 
        LEFT JOIN categories c ON s.category_id = c.id 
        ORDER BY s.id ASC
    """)
    all_schemes = cursor.fetchall()

    matching_schemes, normalized_profile = find_matching_schemes(all_schemes, raw_data)
    saved_ids = get_user_saved_ids(session.get("user_id"))

    return render_template(
        "eligibility_results.html",
        schemes=matching_schemes,
        user_profile=normalized_profile,
        saved_ids=saved_ids
    )


@app.route("/ai_eligibility", methods=["POST"])
def ai_eligibility():
    """
    Extracts structured user profile from natural-language text
    and feeds it into the Python eligibility engine.
    """
    query_text = request.form.get("natural_query", "").strip()
    if not query_text:
        flash("Please provide a brief description of yourself.", "warning")
        return redirect(url_for("eligibility"))

    extracted_profile = extract_user_profile(query_text)

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, c.category 
        FROM schemes s 
        LEFT JOIN categories c ON s.category_id = c.id 
        ORDER BY s.id ASC
    """)
    all_schemes = cursor.fetchall()

    matching_schemes, normalized_profile = find_matching_schemes(all_schemes, extracted_profile)
    saved_ids = get_user_saved_ids(session.get("user_id"))

    return render_template(
        "eligibility_results.html",
        schemes=matching_schemes,
        user_profile=normalized_profile,
        saved_ids=saved_ids
    )


# ==================================================
# USER AUTHENTICATION & SESSIONS
# ==================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """Handles new user registration with secure password hashing."""
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please enter a valid email address.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash("An account with this email address already exists.", "warning")
            return render_template("register.html")

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, 'user')",
            (name, email, hashed_password)
        )
        db.commit()

        flash("Registration successful! Please login to continue.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login and session creation."""
    if session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template("login.html")

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")

            next_url = request.args.get("next")
            return redirect(next_url if next_url and next_url.startswith("/") else url_for("home"))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Logs out user and clears session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("home"))


# ==================================================
# SAVED / BOOKMARKED SCHEMES
# ==================================================

@app.route("/save_scheme/<int:scheme_id>", methods=["POST"])
def save_scheme(scheme_id):
    """Bookmarks a scheme for the authenticated user."""
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to bookmark schemes.", "warning")
        return redirect(url_for("login", next=request.form.get("next", request.referrer)))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "INSERT IGNORE INTO saved_schemes (user_id, scheme_id) VALUES (%s, %s)",
            (user_id, scheme_id)
        )
        db.commit()
        flash("Scheme added to your saved list!", "success")
    except Exception:
        flash("Could not save scheme. Please try again.", "danger")

    next_url = request.form.get("next") or request.referrer or url_for("saved_schemes")
    return redirect(next_url)


@app.route("/unsave_scheme/<int:scheme_id>", methods=["POST"])
def unsave_scheme(scheme_id):
    """Removes a bookmarked scheme for the authenticated user."""
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute(
            "DELETE FROM saved_schemes WHERE user_id = %s AND scheme_id = %s",
            (user_id, scheme_id)
        )
        db.commit()
        flash("Scheme removed from your saved list.", "info")
    except Exception:
        flash("Could not remove saved scheme.", "danger")

    next_url = request.form.get("next") or request.referrer or url_for("saved_schemes")
    return redirect(next_url)


@app.route("/saved_schemes")
def saved_schemes():
    """Displays all schemes bookmarked by the logged-in user."""
    user_id = session.get("user_id")
    if not user_id:
        flash("Please log in to view your saved schemes.", "info")
        return redirect(url_for("login", next=request.path))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT s.*, c.category 
        FROM schemes s 
        JOIN saved_schemes ss ON s.id = ss.scheme_id 
        LEFT JOIN categories c ON s.category_id = c.id 
        WHERE ss.user_id = %s 
        ORDER BY ss.created_at DESC
    """
    cursor.execute(query, (user_id,))
    schemes = cursor.fetchall()
    saved_ids = {s["id"] for s in schemes}

    return render_template("saved_schemes.html", schemes=schemes, saved_ids=saved_ids)


# ==================================================
# CONTACT US & ABOUT US (PUBLIC)
# ==================================================

@app.route("/ContactUs", methods=["POST", "GET"])
def contact():
    """Handles contact inquiries and records them in MySQL."""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not subject or not message:
            flash("All fields are required. Please fill out the form completely.", "danger")
            return redirect(url_for("contact"))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Please provide a valid email address.", "danger")
            return redirect(url_for("contact"))

        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            query = """INSERT INTO contacts(Name, email, subject, message) VALUES (%s, %s, %s, %s);"""
            cursor.execute(query, (name, email, subject, message))
            db.commit()
            flash("Your message has been submitted successfully! We will get back to you soon.", "success")
        except Exception:
            flash("Failed to submit message. Please try again later.", "danger")

        return redirect(url_for("contact"))

    return render_template("contactUs.html")


@app.route("/AboutUs")
def aboutUs():
    """Renders the About Us page."""
    return render_template("AboutUs.html")


# ==================================================
# ADMIN DASHBOARD & MANAGEMENT ROUTES
# ==================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Handles admin authentication against the admins table."""
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template("admin/admin_login.html")

        db = get_db()
        cursor = db.cursor(dictionary=True)

        # Check in admins table first
        cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
        admin = cursor.fetchone()

        # Fallback check in users table for admin role if applicable
        if not admin:
            cursor.execute("SELECT * FROM users WHERE (name = %s OR email = %s) AND role = 'admin'", (username, username))
            user_admin = cursor.fetchone()
            if user_admin and check_password_hash(user_admin["password_hash"], password):
                session["admin_logged_in"] = True
                session["admin_username"] = user_admin["name"]
                session["admin_id"] = user_admin["id"]
                flash("Logged in successfully to Admin Dashboard.", "success")
                next_page = request.args.get("next")
                return redirect(next_page if next_page and next_page.startswith("/admin") else url_for("admin_dashboard"))

        if admin and check_password_hash(admin["password"], password):
            session["admin_logged_in"] = True
            session["admin_username"] = admin["username"]
            session["admin_id"] = admin["id"]
            flash("Logged in successfully to Admin Dashboard.", "success")
            next_page = request.args.get("next")
            return redirect(next_page if next_page and next_page.startswith("/admin") else url_for("admin_dashboard"))
        else:
            flash("Invalid login credentials.", "danger")

    return render_template("admin/admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    """Logs out admin user and clears session."""
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    session.pop("admin_id", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_login_required
def admin_dashboard():
    """
    Main Admin Dashboard overview displaying dynamic statistics from MySQL:
    - Total Schemes
    - Total Categories
    - Total Contact Messages
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM schemes")
    total_schemes = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM categories")
    total_categories = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM contacts")
    total_contacts = cursor.fetchone()["total"]

    # Fetch 5 most recent schemes for quick overview
    cursor.execute("""
        SELECT s.*, c.category 
        FROM schemes s 
        LEFT JOIN categories c ON s.category_id = c.id 
        ORDER BY s.id DESC 
        LIMIT 5
    """)
    recent_schemes = cursor.fetchall()

    return render_template(
        "admin/dashboard.html",
        total_schemes=total_schemes,
        total_categories=total_categories,
        total_contacts=total_contacts,
        recent_schemes=recent_schemes
    )


@app.route("/admin/schemes")
@admin_login_required
def admin_schemes():
    """
    Displays all schemes in a table with search filtering by name and category.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    q = request.args.get("q", "").strip()
    if q:
        query = """
            SELECT s.*, c.category 
            FROM schemes s 
            LEFT JOIN categories c ON s.category_id = c.id 
            WHERE s.scheme_name LIKE %s OR c.category LIKE %s
            ORDER BY s.id DESC
        """
        pattern = f"%{q}%"
        cursor.execute(query, (pattern, pattern))
    else:
        query = """
            SELECT s.*, c.category 
            FROM schemes s 
            LEFT JOIN categories c ON s.category_id = c.id 
            ORDER BY s.id DESC
        """
        cursor.execute(query)

    schemes = cursor.fetchall()

    return render_template(
        "admin/schemes.html",
        schemes=schemes,
        q=q
    )


@app.route("/admin/schemes/add", methods=["GET", "POST"])
@app.route("/admin/scheme/add", methods=["GET", "POST"])
@admin_login_required
def admin_scheme_add():
    """
    Allows admin to manually create and insert a new scheme into the database.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        scheme_name = request.form.get("scheme_name", "").strip()
        category_id = request.form.get("category_id")
        description = request.form.get("description", "").strip()
        eligibility_text = request.form.get("eligibility", "").strip()
        benefits = request.form.get("benefits", "").strip()
        required_document = request.form.get("required_document", "").strip()
        official_link = request.form.get("official_link", "").strip()
        image = request.form.get("image", "Photo/home.jpg").strip() or "Photo/home.jpg"

        # Optional recommendation engine criteria
        min_age = request.form.get("min_age") or None
        max_age = request.form.get("max_age") or None
        max_income = request.form.get("max_income") or None
        gender = request.form.get("gender", "Any")
        farmer = request.form.get("farmer", "Any")
        disability = request.form.get("disability", "Any")
        area_type = request.form.get("area_type", "Any")
        social_category = request.form.get("social_category", "Any")
        house_owner = request.form.get("house_owner", "Any")
        occupation = request.form.get("occupation", "Any")
        state = request.form.get("state", "All")

        if not scheme_name or not category_id or not description or not eligibility_text:
            flash("Please fill in all required scheme fields.", "danger")
            cursor.execute("SELECT * FROM categories ORDER BY category ASC")
            categories = cursor.fetchall()
            return render_template("admin/add_scheme.html", categories=categories)

        query = """
            INSERT INTO schemes (
                scheme_name, category_id, description, eligibility, benefits,
                required_document, official_link, image, min_age, max_age,
                max_income, gender, farmer, disability, area_type,
                social_category, house_owner, occupation, state
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        cursor.execute(query, (
            scheme_name, category_id, description, eligibility_text, benefits,
            required_document, official_link, image, min_age, max_age,
            max_income, gender, farmer, disability, area_type,
            social_category, house_owner, occupation, state
        ))
        db.commit()

        flash("Scheme added successfully.", "success")
        return redirect(url_for("admin_schemes"))

    cursor.execute("SELECT * FROM categories ORDER BY category ASC")
    categories = cursor.fetchall()
    return render_template("admin/add_scheme.html", categories=categories)


@app.route("/admin/schemes/edit/<int:scheme_id>", methods=["GET", "POST"])
@app.route("/admin/scheme/edit/<int:scheme_id>", methods=["GET", "POST"])
@admin_login_required
def admin_scheme_edit(scheme_id):
    """
    Allows admin to modify an existing scheme record.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM schemes WHERE id = %s", (scheme_id,))
    scheme = cursor.fetchone()
    if not scheme:
        flash("Scheme not found.", "warning")
        return redirect(url_for("admin_schemes"))

    if request.method == "POST":
        scheme_name = request.form.get("scheme_name", "").strip()
        category_id = request.form.get("category_id")
        description = request.form.get("description", "").strip()
        eligibility_text = request.form.get("eligibility", "").strip()
        benefits = request.form.get("benefits", "").strip()
        required_document = request.form.get("required_document", "").strip()
        official_link = request.form.get("official_link", "").strip()
        image = request.form.get("image", "").strip() or scheme.get("image") or "Photo/home.jpg"

        min_age = request.form.get("min_age") or None
        max_age = request.form.get("max_age") or None
        max_income = request.form.get("max_income") or None
        gender = request.form.get("gender", "Any")
        farmer = request.form.get("farmer", "Any")
        disability = request.form.get("disability", "Any")
        area_type = request.form.get("area_type", "Any")
        social_category = request.form.get("social_category", "Any")
        house_owner = request.form.get("house_owner", "Any")
        occupation = request.form.get("occupation", "Any")
        state = request.form.get("state", "All")

        if not scheme_name or not category_id or not description or not eligibility_text:
            flash("Please fill in all required fields.", "danger")
            cursor.execute("SELECT * FROM categories ORDER BY category ASC")
            categories = cursor.fetchall()
            return render_template("admin/edit_scheme.html", scheme=scheme, categories=categories)

        query = """
            UPDATE schemes SET
                scheme_name = %s, category_id = %s, description = %s, eligibility = %s, benefits = %s,
                required_document = %s, official_link = %s, image = %s, min_age = %s, max_age = %s,
                max_income = %s, gender = %s, farmer = %s, disability = %s, area_type = %s,
                social_category = %s, house_owner = %s, occupation = %s, state = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            scheme_name, category_id, description, eligibility_text, benefits,
            required_document, official_link, image, min_age, max_age,
            max_income, gender, farmer, disability, area_type,
            social_category, house_owner, occupation, state,
            scheme_id
        ))
        db.commit()

        flash("Scheme updated successfully.", "success")
        return redirect(url_for("admin_schemes"))

    cursor.execute("SELECT * FROM categories ORDER BY category ASC")
    categories = cursor.fetchall()
    return render_template("admin/edit_scheme.html", scheme=scheme, categories=categories)


@app.route("/admin/schemes/delete/<int:scheme_id>", methods=["POST"])
@app.route("/admin/scheme/delete/<int:scheme_id>", methods=["POST"])
@admin_login_required
def admin_scheme_delete(scheme_id):
    """
    Deletes a scheme from the database after confirmation.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM schemes WHERE id = %s", (scheme_id,))
    db.commit()
    flash("Scheme deleted successfully.", "success")
    return redirect(url_for("admin_schemes"))


@app.route("/admin/contacts")
@admin_login_required
def admin_contacts():
    """
    Displays all submitted contact form messages in a table.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts ORDER BY SrNo DESC")
    contacts = cursor.fetchall()
    return render_template("admin/contacts.html", contacts=contacts)


@app.route("/admin/contacts/delete/<int:contact_id>", methods=["POST"])
@admin_login_required
def admin_contact_delete(contact_id):
    """
    Deletes a contact message after confirmation.
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM contacts WHERE SrNo = %s", (contact_id,))
    db.commit()
    flash("Contact message deleted successfully.", "success")
    return redirect(url_for("admin_contacts"))


# Backward-compatible category management routes
@app.route("/admin/categories")
@admin_login_required
def admin_categories():
    """Lists all scheme categories and their associated scheme counts."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    query = """
        SELECT c.*, COUNT(s.id) AS scheme_count 
        FROM categories c 
        LEFT JOIN schemes s ON c.id = s.category_id 
        GROUP BY c.id, c.category 
        ORDER BY c.id ASC
    """
    cursor.execute(query)
    categories = cursor.fetchall()
    return render_template("admin/categories.html", categories=categories)


@app.route("/admin/category/add", methods=["POST"])
@admin_login_required
def admin_category_add():
    """Adds a new scheme category."""
    category_name = request.form.get("category_name", "").strip()
    if category_name:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("INSERT INTO categories (category) VALUES (%s)", (category_name,))
        db.commit()
        flash(f'Category "{category_name}" added successfully.', "success")
    return redirect(url_for("admin_categories"))


@app.route("/admin/category/delete/<int:category_id>", methods=["POST"])
@admin_login_required
def admin_category_delete(category_id):
    """Deletes a category from the database."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
    db.commit()
    flash("Category deleted successfully.", "info")
    return redirect(url_for("admin_categories"))


# ==================================================
# ERROR HANDLERS
# ==================================================

@app.errorhandler(404)
def page_not_found(e):
    flash("The requested page was not found.", "warning")
    return redirect(url_for("home"))


@app.errorhandler(500)
def internal_server_error(e):
    flash("An unexpected internal error occurred. Please try again.", "danger")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)