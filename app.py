from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management
bcrypt = Bcrypt(app)

# Helper functions for JSON storage
def read_users():
    with open("data.json", "r") as file:
        data = json.load(file)
    return data["users"]

def write_users(users):
    with open("data.json", "w") as file:
        json.dump({"users": users}, file, indent=4)

# Routes
@app.route("/")
def home():
    if "username" in session:
        return redirect(url_for("profile_dashboard"))
    return redirect(url_for("index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        users = read_users()
        user = next((u for u in users if u["username"] == username), None)

        if user and bcrypt.check_password_hash(user["password"], password):
            session["username"] = username
            return redirect(url_for("profile_dashboard"))
        else:
            return render_template("index.html", error="Invalid credentials")

    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        users = read_users()
        if any(u["username"] == username for u in users):
            return render_template("register.html", error="Username already exists")

        users.append({"username": username, "password": hashed_password})
        write_users(users)
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route("/profile_dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("index"))
    return render_template("profile_dashboard.html", username=session["username"])

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
