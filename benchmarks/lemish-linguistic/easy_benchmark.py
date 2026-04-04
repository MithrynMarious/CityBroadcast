"""Sample API endpoint with planted vulnerabilities for benchmarking."""
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect("users.db")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    db = get_db()
    # Query user
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query).fetchone()
    if result:
        return jsonify({"status": "ok", "user": result[1], "role": result[3]})
    return jsonify({"status": "fail"}), 401

@app.route("/profile/<user_id>")
def profile(user_id):
    db = get_db()
    user = db.execute(f"SELECT * FROM users WHERE id={user_id}").fetchone()
    return jsonify({"name": user[1], "email": user[2], "role": user[3], "ssn": user[4]})

@app.route("/admin/delete", methods=["POST"])
def delete_user():
    user_id = request.json.get("id")
    db = get_db()
    db.execute(f"DELETE FROM users WHERE id={user_id}")
    db.commit()
    return jsonify({"deleted": user_id})

@app.route("/search")
def search():
    q = request.args.get("q", "")
    return f"<h1>Results for: {q}</h1><p>No results found.</p>"
