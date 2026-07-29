from databases.user_database import UserDatabase
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from routes.utils import login_required, get_database

account_bp = Blueprint("account", __name__)
users = UserDatabase("users.db")

@account_bp.route("/account")
@login_required
def account():
    return render_template("account.html", username=session.get("username"))

@account_bp.route("/change_password", methods=["POST"])
def change_password():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]
    if not users.change_password(session["user_id"],old_password, new_password):
        return render_template("account.html", error="Old password incorrect", username=session.get("username"))

    return render_template("account.html", message="Password changed successfully", username=session.get("username"))

@account_bp.route("/change_username", methods=["POST"])
def change_username():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
    new_username = request.form["new_username"]
    if not users.change_username(session["user_id"], new_username):
        return render_template("account.html", error="Old password incorrect", username=session.get("username"))

    return render_template("account.html", message="Password changed successfully", username=session.get("username"))



@account_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
    user_id = session["user_id"]
    users.delete_user(user_id)
    session.clear()
    return redirect(url_for("auth.login"))


@account_bp.route("/privacy")
@login_required
def privacy():
    db = get_database()
    return jsonify({
        "sharing_enabled": db.get_setting("sharing_enabled"),
        "recommendations_enabled": db.get_setting("recommendations_enabled"),
    })


@account_bp.route("/health")
def health():
    return jsonify({"status": "online", "service": "BookScan"})


@account_bp.route("/settings", methods=["GET"])
@login_required
def settings():
    db = get_database()
    return jsonify({
        "reading_goal": db.get_setting("reading_goal"),
        "sharing_enabled": bool(db.get_setting("sharing_enabled")),
        "recommendations_enabled": bool(db.get_setting("recommendations_enabled")),
        "tailscale_enabled": bool(db.get_setting("tailscale_enabled")),
    })
