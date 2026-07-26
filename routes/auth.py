from databases.user_database import UserDatabase
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session

auth_bp = Blueprint("auth", __name__)

users = UserDatabase("users.db")

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard.dashboard"))

    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if users.verify_user(username, password):
            session.clear()
            session["logged_in"] = True
            session["username"] = username
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

        #TODO: add password methodology for the error messages to be shown
        if users.add_user(username, password):
            session["username"] = username
            session["logged_in"] = True
            return redirect(url_for("dashboard.dashboard"))
        else:
            error = "Username already exists"

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
        "username": session["username"],
        "role": users.get_role(session["username"])
    })

