from flask import Flask, render_template, request, redirect, url_for, session
from databases.database import BookDatabase
from databases.user_database import UserDatabase
import secrets
from messages import get_ratio_message, get_random_greeting, get_random_recommendation
from flask import jsonify
from routes.auth import auth_bp
from routes.utils import login_required, init_all
from routes.account import account_bp
from routes.dashboard import dashboard_bp
from routes.library import library_bp
app = Flask(__name__)
#app.secret_key = secrets.token_hex(32)  # New key every startup
app.secret_key = "Now_same"

app.register_blueprint(auth_bp)
app.register_blueprint(account_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(library_bp)

if __name__ == "__main__":
    init_all()
    app.run(host="0.0.0.0", port=5000)
