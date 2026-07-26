from functools import wraps
from flask import session, redirect, url_for
from databases.database import BookDatabase
from databases.user_database import UserDatabase
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app
 

MOBILE_LOGIN_SALT = "mobile-login"
MOBILE_LOGIN_MAX_AGE = 300  # seconds - QR code is only valid for 5 minutes
DATABASEFOLDER = "databases"
users = UserDatabase("users.db")


def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if not session.get("logged_in"):
            return redirect(
                url_for("auth.login")
            )

        return func(*args, **kwargs)

    return wrapper

def get_database():
    username = session.get("username")
    if not username:
        raise RuntimeError("No logged in user.")
    return BookDatabase(f"{DATABASEFOLDER}/{username}.db")

def init_all():
    os.makedirs(DATABASEFOLDER, exist_ok=True) 
 
def generate_mobile_login_token(username):
    """Create a short-lived signed token that lets a phone log in by
    scanning a QR code, without exposing the actual session/password."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({"username": username}, salt=MOBILE_LOGIN_SALT)
 
 
def verify_mobile_login_token(token):
    """Validate a mobile login token. Returns the username if valid, or
    None if the token is missing, tampered with, or expired."""
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = serializer.loads(token, salt=MOBILE_LOGIN_SALT, max_age=MOBILE_LOGIN_MAX_AGE)
        return data.get("username")
    except (BadSignature, SignatureExpired):
        return None
