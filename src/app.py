from datetime import datetime, timedelta
from pathlib import Path

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)

from .db import get_conn


BUILDINGS = [
    "Toomey Hall",
    "Havener Center",
    "Curtis Laws Wilson Library",
    "Schrenk Hall",
    "Computer Science Building",
    "Norwood Hall",
]


def create_app():
    app = Flask(__name__, template_folder=str(Path(__file__).resolve().parent.parent / "templates"),
                static_folder=str(Path(__file__).resolve().parent.parent / "static"))
    app.config["SECRET_KEY"] = "dev-freebites-secret"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def current_user():
        if "user_id" not in session:
            return None
        return {
            "id": session["user_id"],
            "email": session["email"],
            "role": session["role"],
        }

    def login_required(role=None):
        def decorator(view):
            def wrapped(*args, **kwargs):
                user = current_user()
                if not user:
                    return redirect(url_for("login"))
                if role and user["role"] != role:
                    flash("You are not allowed to access that page.", "error")
                    return redirect(url_for("login"))
                return view(*args, **kwargs)

            wrapped.__name__ = view.__name__
            return wrapped

        return decorator

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    @app.route("/", methods=["GET"])
    def root():
        if "role" in session:
            if session["role"] == "organizer":
                return redirect(url_for("organizer_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            code = request.form.get("code", "").strip()

            with get_conn() as conn:
                cur = conn.execute(
                    "SELECT * FROM users WHERE email = ? AND code = ?",
                    (email, code),
                )
                row = cur.fetchone()

            if not row:
                flash("Invalid email or code. Try again.", "error")
                return render_template("login.html")

            session["user_id"] = row["id"]
            session["email"] = row["email"]
            session["role"] = row["role"]

            if row["role"] == "organizer":
                return redirect(url_for("organizer_dashboard"))
            else:
                return redirect(url_for("student_dashboard"))

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    # ------------------------------------------------------------------
    # Organizer views
    # ------------------------------------------------------------------
    @app.route("/organizer/dashboard")
    @login_required(role="organizer")
    def organizer_dashboard():
        with get_conn() as conn:
            events = conn.execute(
                "SELECT * FROM events ORDER BY event_date, start_time"
            ).fetchall()

            stats = conn.execute(
                """SELECT
                        COUNT(DISTINCT events.id) AS event_count,
                        COUNT(items.id) AS item_count,
                        COALESCE(SUM(items.total_qty), 0) AS total_qty,
                        COALESCE(SUM(items.total_qty - items.remaining_qty), 0) AS claimed
                    FROM events
                    LEFT JOIN items ON items.event_id = events.id
                """
            ).fetchone()

            # Status breakdown for donut chart
            now = datetime.now()
            soon = (now + timedelta(hours=6)).isoformat(sep=" ", timespec="minutes")
            breakdown = conn.execute(
                """SELECT
                        SUM(CASE WHEN expires_at > ? THEN 1 ELSE 0 END) AS available,
                        SUM(CASE WHEN expires_at <= ? THEN 1 ELSE 0 END) AS expired
                    FROM items
                """,
                (soon, soon),
            ).fetchone()

            items = conn.execute(
                """SELECT items.*, events.title AS event_title
                    FROM items
                    JOIN events ON items.event_id = events.id
                    ORDER BY expires_at
                """
            ).fetchall()

        return render_template(
            "organizer_dashboard.html",
            user=current_user(),
            events=events,
            items=items,
            stats=stats,
            breakdown=breakdown,
            buildings=BUILDINGS,
        )

    @app.route("/organizer/event/new", methods=["GET", "POST"])
    @login_required(role="organizer")
    def new_event():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            building = request.form.get("building", "").strip()
            room = request.form.get("room", "").strip()
            event_date = request.form.get("event_date", "").strip()
            start_time = request.form.get("start_time", "").strip()
            end_time = request.form.get("end_time", "").strip()

            if not title or not building or not room:
                flash("Please fill in all required fields.", "error")
                return render_template("organizer_event_form.html", buildings=BUILDINGS)

            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO events (title, building, room, event_date, start_time, end_time)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                    (title, building, room, event_date, start_time, end_time),
                )
                conn.commit()

            flash("Event created.", "success")
            return redirect(url_for("organizer_dashboard"))

        return render_template(
            "organizer_event_form.html",
            buildings=BUILDINGS,
            event=None,
        )

    @app.route("/organizer/event/<int:event_id>/edit", methods=["GET", "POST"])
    @login_required(role="organizer")
    def edit_event(event_id):
        with get_conn() as conn:
            event = conn.execute(
                "SELECT * FROM events WHERE id = ?", (event_id,)
            ).fetchone()

        if not event:
            flash("Event not found.", "error")
            return redirect(url_for("organizer_dashboard"))

        if request.method == "POST":
            title = request.form.get("title", "").strip()
            building = request.form.get("building", "").strip()
            room = request.form.get("room", "").strip()
            event_date = request.form.get("event_date", "").strip()
            start_time = request.form.get("start_time", "").strip()
            end_time = request.form.get("end_time", "").strip()

            with get_conn() as conn:
                conn.execute(
                    """UPDATE events
                           SET title = ?, building = ?, room = ?, event_date = ?, start_time = ?, end_time = ?
                           WHERE id = ?""",
                    (title, building, room, event_date, start_time, end_time, event_id),
                )
                conn.commit()

            flash("Event updated.", "success")
            return redirect(url_for("organizer_dashboard"))

        return render_template(
            "organizer_event_form.html",
            event=event,
            buildings=BUILDINGS,
        )

    @app.route("/organizer/event/<int:event_id>/delete")
    @login_required(role="organizer")
    def delete_event(event_id):
        with get_conn() as conn:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))
            conn.commit()
        flash("Event deleted.", "info")
        return redirect(url_for("organizer_dashboard"))

    @app.route("/organizer/item/new", methods=["GET", "POST"])
    @login_required(role="organizer")
    def new_item():
        with get_conn() as conn:
            events = conn.execute(
                "SELECT * FROM events ORDER BY event_date, start_time"
            ).fetchall()

        if request.method == "POST":
            event_id = request.form.get("event_id")
            name = request.form.get("name", "").strip()
            icon = request.form.get("icon", "").strip()
            total_qty = int(request.form.get("total_qty") or 0)
            expires_at = request.form.get("expires_at", "").strip()

            if not (event_id and name and icon and total_qty > 0 and expires_at):
                flash("Please fill in all fields correctly.", "error")
                return render_template("organizer_item_form.html", events=events)

            with get_conn() as conn:
                conn.execute(
                    """INSERT INTO items (event_id, name, icon, total_qty, remaining_qty, expires_at)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                    (event_id, name, icon, total_qty, total_qty, expires_at),
                )
                conn.commit()

            flash("Item added.", "success")
            return redirect(url_for("organizer_dashboard"))

        return render_template("organizer_item_form.html", events=events)

    # ------------------------------------------------------------------
    # Student views
    # ------------------------------------------------------------------
    @app.route("/student/dashboard")
    @login_required(role="student")
    def student_dashboard():
        user = current_user()
        now = datetime.now()
        soon = (now + timedelta(hours=6)).isoformat(sep=" ", timespec="minutes")

        with get_conn() as conn:
            items = conn.execute(
                """SELECT items.*, events.title AS event_title, events.building, events.room
                    FROM items
                    JOIN events ON items.event_id = events.id
                    WHERE items.remaining_qty > 0
                    ORDER BY items.expires_at
                """
            ).fetchall()

            # Header stats
            total_available = conn.execute(
                "SELECT COUNT(*) AS c FROM items WHERE remaining_qty > 0"
            ).fetchone()["c"]

            expiring_soon = conn.execute(
                "SELECT COUNT(*) AS c FROM items WHERE remaining_qty > 0 AND expires_at <= ?",
                (soon,),
            ).fetchone()["c"]

            my_claims = conn.execute(
                "SELECT COUNT(*) AS c FROM claims WHERE user_id = ?",
                (user["id"],),
            ).fetchone()["c"]

            my_servings = conn.execute(
                "SELECT COALESCE(SUM(qty), 0) AS s FROM claims WHERE user_id = ?",
                (user["id"],),
            ).fetchone()["s"]

        return render_template(
            "student_dashboard.html",
            user=user,
            items=items,
            total_available=total_available,
            expiring_soon=expiring_soon,
            my_claims=my_claims,
            my_servings=my_servings,
        )

    @app.route("/student/browse")
    @login_required(role="student")
    def student_browse():
        with get_conn() as conn:
            events = conn.execute(
                """SELECT events.*, COUNT(items.id) AS item_count
                    FROM events
                    LEFT JOIN items ON items.event_id = events.id
                    GROUP BY events.id
                    ORDER BY event_date, start_time
                """
            ).fetchall()
        return render_template("student_browse.html", events=events, user=current_user())

    @app.route("/student/claims")
    @login_required(role="student")
    def student_claims():
        user = current_user()
        with get_conn() as conn:
            claims = conn.execute(
                """SELECT claims.*, items.name, events.title AS event_title
                    FROM claims
                    JOIN items ON claims.item_id = items.id
                    JOIN events ON items.event_id = events.id
                    WHERE claims.user_id = ?
                    ORDER BY claimed_at DESC
                """,
                (user["id"],),
            ).fetchall()
        return render_template("student_claims.html", claims=claims, user=user)

    # ------------------------------------------------------------------
    # Claim logic with per-user limit of 2 per item
    # ------------------------------------------------------------------
    @app.route("/student/claim/<int:item_id>", methods=["POST"])
    @login_required(role="student")
    def claim_item(item_id):
        user = current_user()

        with get_conn() as conn:
            item = conn.execute(
                "SELECT * FROM items WHERE id = ?", (item_id,)
            ).fetchone()

            if not item:
                flash("Item not found.", "error")
                return redirect(url_for("student_dashboard"))

            if item["remaining_qty"] <= 0:
                flash("Sorry, this item is all gone.", "error")
                return redirect(url_for("student_dashboard"))

            # how many servings this user already has for this item
            row = conn.execute(
                "SELECT COALESCE(SUM(qty), 0) AS taken FROM claims WHERE user_id = ? AND item_id = ?",
                (user["id"], item_id),
            ).fetchone()
            already_taken = row["taken"]
            remaining_user_quota = 2 - already_taken

            if remaining_user_quota <= 0:
                flash("Limit reached: you can only claim 2 of each item.", "error")
                return redirect(url_for("student_dashboard"))

            # they always claim 1 at a time, but respect remaining_qty and quota
            allowed_qty = min(1, item["remaining_qty"], remaining_user_quota)
            if allowed_qty <= 0:
                flash("No servings left to claim.", "error")
                return redirect(url_for("student_dashboard"))

            conn.execute(
                "INSERT INTO claims (user_id, item_id, qty, claimed_at) VALUES (?, ?, ?, ?)",
                (
                    user["id"],
                    item_id,
                    allowed_qty,
                    datetime.now().isoformat(sep=" ", timespec="minutes"),
                ),
            )
            conn.execute(
                "UPDATE items SET remaining_qty = remaining_qty - ? WHERE id = ?",
                (allowed_qty, item_id),
            )
            conn.commit()

        flash("Claimed! Enjoy your free food 🎉", "success")
        return redirect(url_for("student_dashboard"))

    return app
