from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from APP.extensions import db
from APP.models.user import User
from APP.models.parcel import Parcel


admin = Blueprint("admin", __name__, url_prefix="/admin")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@admin.route("/dashboard")
@login_required
def dashboard():

    # Only Admin and Staff can access this dashboard
    if current_user.role not in ["Admin", "Staff"]:
        flash("You are not authorized to access the admin dashboard.", "danger")
        return redirect(url_for("auth.login"))

    # -----------------------------------------------------
    # USER COUNTS
    # -----------------------------------------------------

    total_customers = User.query.filter_by(
        role="Customer"
    ).count()

    total_drivers = User.query.filter_by(
        role="Driver"
    ).count()

    total_staff = User.query.filter_by(
        role="Staff"
    ).count()

    # -----------------------------------------------------
    # PARCEL COUNTS
    # -----------------------------------------------------

    total_parcels = Parcel.query.count()

    pending_parcels = Parcel.query.filter_by(
        status="Pending"
    ).count()

    received_parcels = Parcel.query.filter_by(
        status="Received"
    ).count()

    in_transit_parcels = Parcel.query.filter_by(
        status="In Transit"
    ).count()

    out_for_delivery = Parcel.query.filter_by(
        status="Out for Delivery"
    ).count()

    delivered_parcels = Parcel.query.filter_by(
        status="Delivered"
    ).count()

    # -----------------------------------------------------
    # PAYMENT COUNTS
    # -----------------------------------------------------

    paid_parcels = Parcel.query.filter_by(
        payment_status="Paid"
    ).count()

    unpaid_parcels = Parcel.query.filter(
        (Parcel.payment_status != "Paid") |
        (Parcel.payment_status.is_(None))
    ).count()

    # -----------------------------------------------------
    # REVENUE
    # -----------------------------------------------------

    paid_parcels_list = Parcel.query.filter_by(
        payment_status="Paid"
    ).all()

    total_revenue = sum(
        float(parcel.delivery_charge or 0)
        for parcel in paid_parcels_list
    )

    unpaid_revenue = sum(
        float(parcel.delivery_charge or 0)
        for parcel in Parcel.query.filter(
            (Parcel.payment_status != "Paid") |
            (Parcel.payment_status.is_(None))
        ).all()
    )

    # -----------------------------------------------------
    # RECENT PARCELS
    # -----------------------------------------------------

    recent_parcels = Parcel.query.order_by(
        Parcel.created_at.desc()
    ).limit(10).all()

    # -----------------------------------------------------
    # RECENT DELIVERIES
    # -----------------------------------------------------

    recent_deliveries = Parcel.query.filter_by(
        status="Delivered"
    ).order_by(
        Parcel.updated_at.desc()
    ).limit(5).all()

    return render_template(
        "admin/dashboard.html",

        total_customers=total_customers,
        total_drivers=total_drivers,
        total_staff=total_staff,

        total_parcels=total_parcels,
        pending_parcels=pending_parcels,
        received_parcels=received_parcels,
        in_transit_parcels=in_transit_parcels,
        out_for_delivery=out_for_delivery,
        delivered_parcels=delivered_parcels,

        paid_parcels=paid_parcels,
        unpaid_parcels=unpaid_parcels,

        total_revenue=total_revenue,
        unpaid_revenue=unpaid_revenue,

        recent_parcels=recent_parcels,
        recent_deliveries=recent_deliveries
    )

