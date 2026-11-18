from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path
from optimizer import optimize_seating, calculate_conflicts

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "exam_seating.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            subject TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS halls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            capacity INTEGER NOT NULL CHECK(capacity > 0)
        );

        CREATE TABLE IF NOT EXISTS allocations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            hall_id INTEGER NOT NULL,
            seat_no INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(hall_id) REFERENCES halls(id),
            UNIQUE(student_id),
            UNIQUE(hall_id, seat_no)
        );
        """)


@app.route("/")
def index():
    with get_db() as db:
        students = db.execute("SELECT * FROM students ORDER BY student_no").fetchall()
        halls = db.execute("SELECT * FROM halls ORDER BY name").fetchall()
        allocation_count = db.execute("SELECT COUNT(*) FROM allocations").fetchone()[0]

    total_capacity = sum(hall["capacity"] for hall in halls)
    return render_template(
        "index.html",
        students=students,
        halls=halls,
        allocation_count=allocation_count,
        total_capacity=total_capacity
    )


@app.route("/students/add", methods=["POST"])
def add_student():
    student_no = request.form.get("student_no", "").strip()
    name = request.form.get("name", "").strip()
    subject = request.form.get("subject", "").strip()

    if not all([student_no, name, subject]):
        flash("Please complete all student fields.", "error")
    else:
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO students(student_no, name, subject) VALUES (?, ?, ?)",
                    (student_no, name, subject)
                )
                db.execute("DELETE FROM allocations")
            flash("Student added successfully.", "success")
        except sqlite3.IntegrityError:
            flash("This Student ID already exists.", "error")

    return redirect(url_for("index"))


@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    with get_db() as db:
        db.execute("DELETE FROM allocations")
        db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    flash("Student deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/halls/add", methods=["POST"])
def add_hall():
    name = request.form.get("name", "").strip()

    try:
        capacity = int(request.form.get("capacity", "0"))
    except ValueError:
        capacity = 0

    if not name or capacity <= 0:
        flash("Enter a hall name and a positive seat capacity.", "error")
    else:
        try:
            with get_db() as db:
                db.execute(
                    "INSERT INTO halls(name, capacity) VALUES (?, ?)",
                    (name, capacity)
                )
                db.execute("DELETE FROM allocations")
            flash("Hall added successfully.", "success")
        except sqlite3.IntegrityError:
            flash("A hall with this name already exists.", "error")

    return redirect(url_for("index"))


@app.route("/halls/<int:hall_id>/delete", methods=["POST"])
def delete_hall(hall_id):
    with get_db() as db:
        db.execute("DELETE FROM allocations")
        db.execute("DELETE FROM halls WHERE id = ?", (hall_id,))
    flash("Hall deleted successfully.", "success")
    return redirect(url_for("index"))


@app.route("/generate", methods=["POST"])
def generate():
    with get_db() as db:
        students = db.execute("SELECT * FROM students ORDER BY student_no").fetchall()
        halls = db.execute("SELECT * FROM halls ORDER BY name").fetchall()

        db.execute("DELETE FROM allocations")

        if not students:
            flash("Please add students before generating a seating plan.", "error")
            return redirect(url_for("index"))

        if not halls:
            flash("Please add at least one exam hall.", "error")
            return redirect(url_for("index"))

        total_capacity = sum(hall["capacity"] for hall in halls)
        if len(students) > total_capacity:
            flash(
                f"Insufficient seats. Students: {len(students)}, total capacity: {total_capacity}.",
                "error"
            )
            return redirect(url_for("index"))

        assignments = optimize_seating(
            [dict(student) for student in students],
            [dict(hall) for hall in halls]
        )

        for assignment in assignments:
            db.execute(
                """INSERT INTO allocations(student_id, hall_id, seat_no)
                   VALUES (?, ?, ?)""",
                (
                    assignment["student_id"],
                    assignment["hall_id"],
                    assignment["seat_no"]
                )
            )

    flash("The seating plan was generated successfully.", "success")
    return redirect(url_for("results"))



@app.route("/results")
def results():
    with get_db() as db:
        rows = db.execute("""
            SELECT s.student_no, s.name, s.subject,
                   h.id AS hall_id,
                   h.name AS hall_name,
                   a.seat_no
            FROM allocations a
            JOIN students s ON s.id = a.student_id
            JOIN halls h ON h.id = a.hall_id
            ORDER BY h.name, a.seat_no
        """).fetchall()

    result_data = [dict(row) for row in rows]

    conflict_score = calculate_conflicts(result_data)

    return render_template(
        "results.html",
        rows=result_data,
        conflict_score=conflict_score
    )



@app.route("/reset", methods=["POST"])
def reset_allocations():
    with get_db() as db:
        db.execute("DELETE FROM allocations")
    flash("The seating allocation has been reset.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
