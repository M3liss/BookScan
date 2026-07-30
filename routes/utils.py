from functools import wraps
from flask import session, redirect, url_for
from databases.database import BookDatabase
from databases.user_database import UserDatabase
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
from flask import g

MOBILE_LOGIN_SALT = "mobile-login"
MOBILE_LOGIN_MAX_AGE = 300
DATABASEFOLDER = "databases"

users = UserDatabase()

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)
    return wrapper

def get_database():
    user_id = session.get("user_id")
    if not user_id:
        raise RuntimeError("No logged in user.")
    if users.get_role(user_id) is None:
        session.clear()
        raise RuntimeError("User no longer exists.")
    if "book_db" not in g:
        g.book_db = BookDatabase(DATABASEFOLDER, user_id)
    return g.book_db

def init_all():
    users = UserDatabase()
    os.makedirs(DATABASEFOLDER, exist_ok=True) 
 
def generate_mobile_login_token(user_id):
    """Create a short-lived signed token that lets a phone log in by
    scanning a QR code, without exposing the actual session/password."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"user_id": user_id}, salt=MOBILE_LOGIN_SALT)
 
 
def verify_mobile_login_token(token):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = serializer.loads(token, salt=MOBILE_LOGIN_SALT, max_age=MOBILE_LOGIN_MAX_AGE)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None


def start_session(user_id, username):
    session.clear()
    session["logged_in"] = True
    session["user_id"] = user_id
    session["username"] = username

def change_username(user_id, username):
    #TODO
    return 1