import os
import socket
from functools import wraps
from urllib.parse import urlsplit, urlunsplit

from flask import current_app, g, redirect, session, url_for
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from databases.database import BookDatabase
from databases.user_database import UserDatabase

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
 
def _get_secret_key():
    try:
        return current_app.config["SECRET_KEY"]
    except RuntimeError:
        return os.environ.get("SECRET_KEY")


def discover_local_ip():
    env_host = os.environ.get("BOOKSCAN_HOST") or os.environ.get("HOST")
    if env_host:
        return env_host

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            candidate = sock.getsockname()[0]
            if candidate and not candidate.startswith("127.") and not candidate.startswith("169.254."):
                return candidate
    except OSError:
        pass

    for host in (socket.gethostname(), "localhost"):
        try:
            infos = socket.getaddrinfo(host, None, socket.AF_INET, socket.SOCK_DGRAM)
            for info in infos:
                ip = info[4][0]
                if ip and not ip.startswith("127.") and not ip.startswith("169.254."):
                    return ip
        except OSError:
            continue

    return None


def build_mobile_scan_url(path, request=None):
    if request is None:
        return path

    parsed = urlsplit(request.host_url)
    host = parsed.hostname or "localhost"
    port = parsed.port or request.environ.get("SERVER_PORT") or 5000
    if host in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        lan_ip = discover_local_ip()
        if lan_ip:
            host = lan_ip

    if port in {80, 443}:
        netloc = host
    else:
        netloc = f"{host}:{port}"

    return urlunsplit((parsed.scheme, netloc, path, "", ""))


def generate_mobile_login_token(user_id, username=None):
    """Create a short-lived signed token that lets a phone log in by
    scanning a QR code, without exposing the actual session/password."""
    serializer = URLSafeTimedSerializer(_get_secret_key())
    payload = {"user_id": user_id}
    if username is not None:
        payload["username"] = username
    return serializer.dumps(payload, salt=MOBILE_LOGIN_SALT)


def verify_mobile_login_token(token):
    serializer = URLSafeTimedSerializer(_get_secret_key())
    try:
        data = serializer.loads(token, salt=MOBILE_LOGIN_SALT, max_age=MOBILE_LOGIN_MAX_AGE)
        if not isinstance(data, dict):
            return None
        return data
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