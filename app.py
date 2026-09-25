import os
from flask import Flask
from dotenv import load_dotenv
from APP.extensions import db, migrate, login_manager
from APP.models.user import User
from APP.models.parcel import Parcel

load_dotenv()

app = Flask(__name__, template_folder="APP/templates", static_folder="APP/static")

# Config
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-2024")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL") or "mysql+pymysql://root@localhost/parcel_drop"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init extensions
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Login loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
from APP.routes.auth import auth
from APP.routes.parcels import parcels
from APP.routes.drivers import drivers
from APP.routes.admin import admin
from APP.routes.reports import reports

app.register_blueprint(auth)
app.register_blueprint(parcels)
app.register_blueprint(drivers)
app.register_blueprint(admin)
app.register_blueprint(reports)

# Home route
@app.route("/")
def home():
    return "<h1>Parcel Drop System</h1><p><a href='/login'>Login</a></p>"

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)