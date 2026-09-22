import os
from urllib.parse import quote_plus

from flask import Flask
from dotenv import load_dotenv

from APP.extensions import db, migrate, login_manager


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CREATE APPLICATION
# ============================================================

def create_app():

    app = Flask(
        __name__,
        template_folder="APP/templates",
        static_folder="APP/static"
    )

    # ========================================================
    # APPLICATION CONFIGURATION
    # ========================================================

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-secret-key"
    )

    # ========================================================
    # DATABASE CONFIGURATION
    # ========================================================

    db_user = os.getenv("DB_USER")

    db_password = quote_plus(
        os.getenv("DB_PASSWORD", "")
    )

    db_host = os.getenv("DB_HOST")

    db_port = os.getenv(
        "DB_PORT",
        "3306"
    )

    db_name = os.getenv("DB_NAME")

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://"
        f"{db_user}:{db_password}@"
        f"{db_host}:{db_port}/"
        f"{db_name}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ========================================================
    # INITIALIZE FLASK EXTENSIONS
    # ========================================================

    db.init_app(app)

    migrate.init_app(
        app,
        db
    )

    login_manager.init_app(
        app
    )

    # ========================================================
    # IMPORT MODELS
    # ========================================================

    from APP.models.user import User
    from APP.models.parcel import Parcel

    # ========================================================
    # LOGIN MANAGER
    # ========================================================

    @login_manager.user_loader
    def load_user(user_id):

        return User.query.get(
            int(user_id)
        )

    # ========================================================
    # REGISTER PARCEL ROUTES
    # ========================================================

    from APP.routes.parcels import parcels

    app.register_blueprint(
        parcels
    )

    # ========================================================
    # REGISTER AUTHENTICATION ROUTES
    # ========================================================

    from APP.routes.auth import auth

    app.register_blueprint(
        auth
    )

    # ========================================================
    # REGISTER DRIVER ROUTES
    # ========================================================

    from APP.routes.drivers import drivers

    app.register_blueprint(
        drivers
    )

    from APP.routes.admin import admin

    app.register_blueprint(
        admin
    )

    from APP.routes.reports import reports
    app.register_blueprint(
        reports
    )

    # ========================================================
    # HOME PAGE
    # ========================================================

    @app.route("/")
    def home():

        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Parcel Drop System</title>
        </head>

        <body>

            <h1>Parcel Drop System</h1>

            <p>
                Welcome to the Parcel Drop System.
            </p>

            <p>
                <a href="/book">
                    Book a Parcel
                </a>
            </p>

        </body>
        </html>
        """

    # ========================================================
    # RETURN APPLICATION
    # ========================================================

    return app


# ============================================================
# APPLICATION INSTANCE
# ============================================================

app = create_app()


# ============================================================
# RUN APPLICATION DIRECTLY
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )