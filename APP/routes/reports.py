from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from APP.models.parcel import Parcel
from APP.models.user import User


reports = Blueprint("reports", __name__, url_prefix="/reports")


@reports.route("/")
@login_required
def reports_page():

    # ---------------------------------------------------------
    # ACCESS CONTROL
    # ---------------------------------------------------------

    if current_user.role not in ["Admin", "Staff"]:
        flash("You are not authorized to access reports.", "danger")
        return redirect(url_for("auth.login"))

    # ---------------------------------------------------------
    # FILTERS
    # ---------------------------------------------------------

    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    status = request.args.get("status", "").strip()
    payment_status = request.args.get("payment_status", "").strip()

    query = Parcel.query

    # ---------------------------------------------------------
    # DATE FILTER
    # ---------------------------------------------------------

    if start_date:
        try:
            start_datetime = datetime.strptime(
                start_date,
                "%Y-%m-%d"
            )

            query = query.filter(
                Parcel.created_at >= start_datetime
            )

        except ValueError:
            flash("Invalid start date.", "danger")

    if end_date:
        try:
            end_datetime = datetime.strptime(
                end_date,
                "%Y-%m-%d"
            )

            # Include the entire end date
            end_datetime = end_datetime.replace(
                hour=23,
                minute=59,
                second=59
            )

            query = query.filter(
                Parcel.created_at <= end_datetime
            )

        except ValueError:
            flash("Invalid end date.", "danger")

    # ---------------------------------------------------------
    # STATUS FILTER
    # ---------------------------------------------------------

    if status:
        query = query.filter(
            Parcel.status == status
        )

    # ---------------------------------------------------------
    # PAYMENT FILTER
    # ---------------------------------------------------------

    if payment_status:
        query = query.filter(
            Parcel.payment_status == payment_status
        )

    # ---------------------------------------------------------
    # GET FILTERED PARCELS
    # ---------------------------------------------------------

    parcels = query.order_by(
        Parcel.created_at.desc()
    ).all()

    # ---------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------

    total_parcels = len(parcels)

    pending_count = sum(
        1 for parcel in parcels
        if parcel.status == "Pending"
    )

    received_count = sum(
        1 for parcel in parcels
        if parcel.status == "Received"
    )

    in_transit_count = sum(
        1 for parcel in parcels
        if parcel.status == "In Transit"
    )

    out_for_delivery_count = sum(
        1 for parcel in parcels
        if parcel.status == "Out for Delivery"
    )

    delivered_count = sum(
        1 for parcel in parcels
        if parcel.status == "Delivered"
    )

    paid_count = sum(
        1 for parcel in parcels
        if parcel.payment_status == "Paid"
    )

    unpaid_count = total_parcels - paid_count

    # ---------------------------------------------------------
    # REVENUE
    # ---------------------------------------------------------

    total_revenue = sum(
        float(parcel.delivery_charge or 0)
        for parcel in parcels
        if parcel.payment_status == "Paid"
    )

    outstanding_revenue = sum(
        float(parcel.delivery_charge or 0)
        for parcel in parcels
        if parcel.payment_status != "Paid"
    )

    total_charges = sum(
        float(parcel.delivery_charge or 0)
        for parcel in parcels
    )

    # ---------------------------------------------------------
    # PAYMENT METHODS
    # ---------------------------------------------------------

    mpesa_count = sum(
        1 for parcel in parcels
        if parcel.payment_method == "M-Pesa"
    )

    cash_count = sum(
        1 for parcel in parcels
        if parcel.payment_method == "Cash"
    )

    card_count = sum(
        1 for parcel in parcels
        if parcel.payment_method == "Card"
    )

    bank_count = sum(
        1 for parcel in parcels
        if parcel.payment_method == "Bank Transfer"
    )

    # ---------------------------------------------------------
    # DRIVER REPORT
    # ---------------------------------------------------------

    drivers = User.query.filter_by(
        role="Driver"
    ).order_by(
        User.name.asc()
    ).all()

    driver_reports = []

    for driver in drivers:

        driver_parcels = [
            parcel
            for parcel in parcels
            if parcel.assigned_driver_id == driver.id
        ]

        driver_reports.append({
            "driver": driver,
            "total": len(driver_parcels),
            "pending": sum(
                1 for parcel in driver_parcels
                if parcel.status == "Pending"
            ),
            "in_transit": sum(
                1 for parcel in driver_parcels
                if parcel.status == "In Transit"
            ),
            "out_for_delivery": sum(
                1 for parcel in driver_parcels
                if parcel.status == "Out for Delivery"
            ),
            "delivered": sum(
                1 for parcel in driver_parcels
                if parcel.status == "Delivered"
            ),
        })

    # ---------------------------------------------------------
    # AVAILABLE FILTER VALUES
    # ---------------------------------------------------------

    statuses = [
        "Pending",
        "Received",
        "In Transit",
        "Out for Delivery",
        "Delivered"
    ]

    payment_statuses = [
        "Paid",
        "Unpaid"
    ]

    return render_template(
        "admin/reports.html",

        parcels=parcels,

        total_parcels=total_parcels,

        pending_count=pending_count,
        received_count=received_count,
        in_transit_count=in_transit_count,
        out_for_delivery_count=out_for_delivery_count,
        delivered_count=delivered_count,

        paid_count=paid_count,
        unpaid_count=unpaid_count,

        total_revenue=total_revenue,
        outstanding_revenue=outstanding_revenue,
        total_charges=total_charges,

        mpesa_count=mpesa_count,
        cash_count=cash_count,
        card_count=card_count,
        bank_count=bank_count,

        driver_reports=driver_reports,

        statuses=statuses,
        payment_statuses=payment_statuses,

        start_date=start_date,
        end_date=end_date,
        selected_status=status,
        selected_payment_status=payment_status
    )

