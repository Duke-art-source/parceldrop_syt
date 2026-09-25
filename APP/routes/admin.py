from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from APP.extensions import db
from APP.models.user import User
from APP.models.parcel import Parcel


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

