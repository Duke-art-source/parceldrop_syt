from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from APP.extensions import db
from APP.models.user import User
from APP.models.parcel import Parcel
from app import app, db


admin = Blueprint("admin", __name__, url_prefix="/admin")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin.route("/admin-dashboard")
@login_required
def dashboard():
    if current_user.role != "Admin":
        return redirect(url_for("home"))
    
    total_parcels = Parcel.query.count()
    total_users = User.query.count()
    
    return render_template(
        "admin_dashboard.html",
        total_parcels=total_parcels,
        total_users=total_users
    )


with app.app_context():
    # Admin
    admin = User(name="Admin", email="admin@test.com", role="Admin")
    admin.set_password("admin123")
    db.session.add(admin)
    
    # Driver
    driver = User(name="John Driver", email="driver@test.com", role="Driver")
    driver.set_password("driver123")
    db.session.add(driver)
    
    # Customer
    customer = User(name="Jane Customer", email="customer@test.com", role="Customer")
    customer.set_password("customer123")
    db.session.add(customer)
    
    db.session.commit()
    print("✅ All users created!")

