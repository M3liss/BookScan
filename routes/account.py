from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from routes.utils import login_required, get_database, users
from services.sharing import SharingService

account_bp = Blueprint("account", __name__)
sharing_service = SharingService()

@account_bp.route("/account")
@login_required
def account():
    db = get_database()
    return render_template("account.html", username=session.get("username"), sharing_enabled=db.get_setting(session["user_id"], "sharing_enabled"), recommendations_enabled=db.get_setting(session["user_id"], "recommendations_enabled"))

@account_bp.route("/change_password", methods=["POST"])
@login_required
def change_password():
    db = get_database()
    old_password = request.form["old_password"]
    new_password = request.form["new_password"]
    if not users.change_password(session["user_id"],old_password, new_password):
        return render_template("account.html", error="Old password incorrect", username=session.get("username"), sharing_enabled=db.get_setting(session["user_id"], "sharing_enabled"), recommendations_enabled=db.get_setting(session["user_id"], "recommendations_enabled"))

    return render_template("account.html", message="Password changed successfully", username=session.get("username"), sharing_enabled=db.get_setting(session["user_id"], "sharing_enabled"), recommendations_enabled=db.get_setting(session["user_id"], "recommendations_enabled"))

@account_bp.route("/change_username", methods=["POST"])
@login_required
def change_username():
    db = get_database()
    new_username = request.form["new_username"]
    print(f"new usermane: {new_username}")
    if not users.change_username(session["user_id"], new_username):
        return render_template("account.html", error="Username already taken", username=session.get("username"), sharing_enabled=db.get_setting(session["user_id"], "sharing_enabled"), recommendations_enabled=db.get_setting(session["user_id"], "recommendations_enabled"))
    session["username"] = new_username
    return render_template("account.html", message="Username changed successfully", username=session.get("username"), sharing_enabled=db.get_setting(session["user_id"], "sharing_enabled"), recommendations_enabled=db.get_setting(session["user_id"], "recommendations_enabled"))

@account_bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    user_id = session["user_id"]
    users.delete_user(user_id)
    session.clear()
    return redirect(url_for("auth.login"))


@account_bp.route("/change_privacy", methods=["POST"])
@login_required
def set_privacy():
    db = get_database()
    sharing_enabled = request.form.get("sharing_enabled") is not None
    recommendations_enabled = request.form.get("recommendations_enabled") is not None

    db.set_setting(session["user_id"], "sharing_enabled", int(sharing_enabled))
    db.set_setting(session["user_id"], "recommendations_enabled", int(recommendations_enabled))

    sharing_result = sharing_service.enable_sharing(session["user_id"], sharing_enabled)
    recommendations_result = sharing_service.enable_recommendations(session["user_id"]) if recommendations_enabled else {"ok": True, "status": "disabled"}

    return render_template(
        "account.html",
        message="Privacy settings updated successfully",
        username=session.get("username"),
        sharing_enabled=sharing_enabled,
        recommendations_enabled=recommendations_enabled,
        sharing_status=sharing_result,
        recommendations_status=recommendations_result,
    )

@account_bp.route("/health")
def health():
    return jsonify({"status": "online", "service": "BookScan"})


@account_bp.route("/settings", methods=["GET"])      
@login_required
def settings():
    db = get_database()
    sharing_enabled = bool(db.get_setting(session["user_id"], "sharing_enabled"))
    recommendations_enabled = bool(db.get_setting(session["user_id"], "recommendations_enabled"))

    return jsonify({
        "reading_goal": db.get_setting(session["user_id"], "reading_goal"),
        "sharing_enabled": sharing_enabled,
        "recommendations_enabled": recommendations_enabled,
        "tailscale_enabled": bool(db.get_setting(session["user_id"], "tailscale_enabled")),
        "sharing_status": sharing_service.enable_sharing(session["user_id"], sharing_enabled),
        "recommendations_status": sharing_service.enable_recommendations(session["user_id"]) if recommendations_enabled else {"ok": True, "status": "disabled"},
    })


@account_bp.route("/sharing/profile", methods=["GET"])
@login_required
def public_profile():
    db = get_database()
    profile = sharing_service.build_public_profile(session["user_id"], db, session.get("username"))
    return jsonify(profile)


@account_bp.route("/sharing/backup", methods=["POST"])
@login_required
def upload_backup():
    backup_file = request.files.get("backup")
    backup_path = backup_file.filename if backup_file else None
    result = sharing_service.upload_backup(session["user_id"], backup_path)
    return jsonify(result)
