from flask import Flask
import secrets

from routes.auth import auth_bp
from routes.account import account_bp
from routes.dashboard import dashboard_bp
from routes.library import library_bp
from routes.utils import init_all


def create_app():

    app = Flask(__name__)

    app.secret_key = "Now_same"

    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(library_bp)

    init_all()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )