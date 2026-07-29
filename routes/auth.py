from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from routes.utils import users
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard.dashboard"))
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login_user(username, password):
            session.clear()
            session["logged_in"] = True
            session["user_id"] = users.get_user_id(username)
            return redirect(url_for("dashboard.dashboard"))
        else:
            error = "Invalid username or password"

    return render_template("login.html", error=error)

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("logged_in"):
        return redirect(url_for("dashboard.dashboard"))
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.add_user(username, password):
            error = "Username already exists"
        else:
            session["username"] = username
            session["logged_in"] = True
            return redirect(url_for("dashboard.dashboard"))

    return render_template("signup.html", error=error)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/whoami")
def whoami():

    if not session.get("logged_in"):
        return jsonify({
            "logged_in": False
        })

    return jsonify({
        "logged_in": True,
        "user_id": session["user_id"],
        "role": users.get_role(session["user_id"])
    })