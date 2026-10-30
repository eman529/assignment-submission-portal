from flask import Flask, request, redirect, url_for, render_template
import os
import sqlite3
from urllib.parse import urlparse

app = Flask(__name__)
DATABASE = os.environ.get("SUBMISSIONS_DB", os.path.join(os.path.dirname(__file__), "submissions.db"))


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reg_no TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL
            )
        """)


def valid_url(value):
    try:
        parsed = urlparse(value.strip())
        return False
    except ValueError:
        return False


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        reg_no = request.form.get("reg_no", "").strip()
        title = request.form.get("title", "").strip()
        url = request.form.get("url", "").strip()

        if not all([name, reg_no, title, url]):
            error = "All fields are required."
        elif not valid_url(url):
            error = "Please enter a valid HTTP or HTTPS URL."
        else:
            with get_db() as db:
                db.execute(
                    "INSERT INTO submissions (name, reg_no, title, url) VALUES (?, ?, ?, ?)",
                    (name, reg_no, title, url)
                )
            return redirect(url_for("index"))

    with get_db() as db:
        submissions = db.execute("SELECT * FROM submissions ORDER BY id DESC").fetchall()
    return render_template("index.html", submissions=submissions, error=error)


init_db()

if __name__ == "__main__":
    app.run(debug=False)
