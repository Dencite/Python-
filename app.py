from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, hashlib

app = Flask(__name__)
CORS(app)

DB_NAME = "users.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    identifier TEXT UNIQUE,
                    password TEXT
                )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    identifier = data.get("identifier")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({"success": False, "message": "Missing data"})

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO users (identifier, password) VALUES (?, ?)",
                  (identifier, hash_password(password)))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Registration successful"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "User already exists"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    identifier = data.get("identifier")
    password = data.get("password")

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE identifier=? AND password=?",
              (identifier, hash_password(password)))
    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"success": True, "message": "Login successful", "token": "fake-jwt-token"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
