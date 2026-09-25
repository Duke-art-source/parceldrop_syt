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
        "dev-secret-key-change-in-production"
    )

    # =========================================================
    # DATABASE CONFIGURATION
    # =========================================================

    database_url = os.getenv("DATABASE_URL")

    if database_url and database_url.strip():
        if database_url.startswith("mysql://"):
            database_url = database_url.replace(
                "mysql://",
                "mysql+pymysql://",
                1
            )
        print(f"[Railway] Using MySQL connection: {database_url[:50]}...")
    else:
        db_user = os.getenv("DB_USER", "root")
        db_password = quote_plus(os.getenv("DB_PASSWORD", ""))
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "3306")
        db_name = os.getenv("DB_NAME", "parcel_drop")

        database_url = (
            f"mysql+pymysql://"
            f"{db_user}:{db_password}@"
            f"{db_host}:{db_port}/"
            f"{db_name}"
        )
        print(f"[Local] Connecting to MySQL: {db_host}")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 10,
        "pool_recycle": 3600,
        "pool_pre_ping": True,
    }

    # ========================================================
    # INITIALIZE FLASK EXTENSIONS
    # ========================================================

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ========================================================
    # IMPORT MODELS
    # ========================================================

    from APP.models.user import User
    from APP.models.parcel import Parcel

    # ========================================================
    # CREATE DATABASE TABLES ON STARTUP
    # ========================================================

    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"⚠️ Error creating tables: {e}")

    # ========================================================
    # LOGIN MANAGER
    # ========================================================

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ========================================================
    # REGISTER BLUEPRINTS
    # ========================================================

    from APP.routes.parcels import parcels
    from APP.routes.auth import auth
    from APP.routes.drivers import drivers
    from APP.routes.admin import admin
    from APP.routes.reports import reports

    app.register_blueprint(parcels)
    app.register_blueprint(auth)
    app.register_blueprint(drivers)
    app.register_blueprint(admin)
    app.register_blueprint(reports)

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
            <p>Welcome to the Parcel Drop System.</p>
            <p><a href="/login">Login</a></p>
            <p><a href="/book">Book a Parcel</a></p>
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
    port = int(os.getenv("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )