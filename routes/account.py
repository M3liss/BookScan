from databases.user_database import UserDatabase
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from routes.utils import login_required

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
    username = session["username"]
    if not users.verify_user(username, old_password):
        return render_template("account.html", error="Old password incorrect", username=session.get("username"))
    #TODO: add functionality to show if the new password is not big enough / the same as before
    users.change_password(username,new_password)
    return render_template("account.html", message="Password changed successfully", username=session.get("username"))


@account_bp.route("/delete_account", methods=["POST"])
def delete_account():
    if not session.get("logged_in"):
        return redirect(url_for("auth.login"))
    username = session["username"]
    users.delete_user(username)
    session.clear()
    return redirect(url_for("auth.login"))
