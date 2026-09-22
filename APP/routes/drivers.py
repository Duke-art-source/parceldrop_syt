from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func

from APP.extensions import db
from APP.models.user import User
from APP.models.parcel import Parcel


drivers = Blueprint("drivers", __name__)


# =========================================================
# ACCESS CONTROL
# =========================================================

def staff_or_admin_required():
    return (
        current_user.is_authenticated
        and current_user.role in ["Admin", "Staff"]
    )


def driver_required():
    return (
        current_user.is_authenticated
        and current_user.role == "Driver"
    )


# =========================================================
# DRIVER LIST
# =========================================================

@drivers.route("/drivers")
@login_required
def drivers_page():

    if not staff_or_admin_required():
        flash("You are not authorized to access driver management.", "danger")
        return redirect(url_for("parcels.track_parcel"))

    driver_list = User.query.filter_by(
        role="Driver"
    ).order_by(
        User.id.desc()
    ).all()

    return render_template(
        "drivers.html",
        drivers=driver_list
    )


# =========================================================
# CREATE DRIVER
# =========================================================

@drivers.route("/drivers/create", methods=["GET", "POST"])
@login_required
def create_driver():

    if not staff_or_admin_required():
        flash("You are not authorized to create drivers.", "danger")
        return redirect(url_for("parcels.track_parcel"))

    if request.method == "POST":

        print("\n==============================")
        print("CREATE DRIVER POST RECEIVED")
        print("==============================")
        print("FORM DATA:", dict(request.form))

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "").strip()

        print("NAME:", name)
        print("EMAIL:", email)
        print("PHONE:", phone)
        print("PASSWORD PROVIDED:", bool(password))

        # -----------------------------------------
        # VALIDATION
        # -----------------------------------------

        if not name:
            print("ERROR: NAME IS EMPTY")
            flash("Driver name is required.", "danger")
            return redirect(url_for("drivers.create_driver"))

        if not email:
            print("ERROR: EMAIL IS EMPTY")
            flash("Driver email is required.", "danger")
            return redirect(url_for("drivers.create_driver"))

        if not phone:
            print("ERROR: PHONE IS EMPTY")
            flash("Driver phone number is required.", "danger")
            return redirect(url_for("drivers.create_driver"))

        if not password:
            print("ERROR: PASSWORD IS EMPTY")
            flash("Driver password is required.", "danger")
            return redirect(url_for("drivers.create_driver"))

        if len(password) < 6:
            print("ERROR: PASSWORD TOO SHORT")
            flash("Driver password must be at least 6 characters.", "danger")
            return redirect(url_for("drivers.create_driver"))

        # -----------------------------------------
        # CHECK DUPLICATE EMAIL
        # -----------------------------------------

        existing_user = User.query.filter(
            func.lower(User.email) == email
        ).first()

        if existing_user:
            print("ERROR: EMAIL ALREADY EXISTS")
            print("EXISTING USER:", existing_user.id, existing_user.email)

            flash(
                f"The email {email} is already registered.",
                "danger"
            )

            return redirect(
                url_for("drivers.create_driver")
            )

        # -----------------------------------------
        # CREATE DRIVER
        # -----------------------------------------

        try:

            driver = User(
                name=name,
                email=email,
                phone=phone,
                role="Driver",
                status=True
            )

            driver.set_password(password)

            print("PASSWORD HASH CREATED:", bool(driver.password))

            db.session.add(driver)

            print("DRIVER ADDED TO SESSION")

            db.session.commit()

            print("==============================")
            print("DRIVER CREATED SUCCESSFULLY")
            print("ID:", driver.id)
            print("NAME:", driver.name)
            print("EMAIL:", driver.email)
            print("ROLE:", driver.role)
            print("==============================\n")

            flash(
                f"Driver {name} created successfully.",
                "success"
            )

            return redirect(
                url_for("drivers.drivers_page")
            )

        except Exception as e:

            db.session.rollback()

            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("DRIVER CREATION FAILED")
            print("ERROR TYPE:", type(e).__name__)
            print("ERROR:", str(e))
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")

            flash(
                f"Unable to create driver: {str(e)}",
                "danger"
            )

            return redirect(
                url_for("drivers.create_driver")
            )

    return render_template("create_driver.html")


# =========================================================
# DRIVER DASHBOARD
# =========================================================

@drivers.route("/driver-dashboard")
@login_required
def driver_dashboard():

    if not driver_required():
        flash("Driver access required.", "danger")
        return redirect(url_for("parcels.track_parcel"))

    assigned_parcels = Parcel.query.filter_by(
        assigned_driver_id=current_user.id
    ).order_by(
        Parcel.created_at.desc()
    ).all()

    total = len(assigned_parcels)

    pending = sum(
        1 for p in assigned_parcels
        if p.status == "Pending"
    )

    received = sum(
        1 for p in assigned_parcels
        if p.status == "Received"
    )

    in_transit = sum(
        1 for p in assigned_parcels
        if p.status == "In Transit"
    )

    out_for_delivery = sum(
        1 for p in assigned_parcels
        if p.status == "Out for Delivery"
    )

    delivered = sum(
        1 for p in assigned_parcels
        if p.status == "Delivered"
    )

    return render_template(
        "driver_dashboard.html",
        parcels=assigned_parcels,
        total=total,
        pending=pending,
        received=received,
        in_transit=in_transit,
        out_for_delivery=out_for_delivery,
        delivered=delivered
    )


# =========================================================
# DRIVER UPDATE STATUS
# =========================================================

@drivers.route(
    "/driver/parcel/<int:parcel_id>/status",
    methods=["POST"]
)
@login_required
def update_driver_status(parcel_id):

    if not driver_required():
        flash("Driver access required.", "danger")
        return redirect(url_for("parcels.track_parcel"))

    parcel = Parcel.query.get_or_404(parcel_id)

    if parcel.assigned_driver_id != current_user.id:
        flash(
            "This parcel is not assigned to you.",
            "danger"
        )
        return redirect(
            url_for("drivers.driver_dashboard")
        )

    new_status = request.form.get(
        "status",
        ""
    ).strip()

    allowed_statuses = [
        "Pending",
        "Received",
        "In Transit",
        "Out for Delivery",
        "Delivered"
    ]

    if new_status not in allowed_statuses:
        flash(
            "Invalid delivery status.",
            "danger"
        )
        return redirect(
            url_for("drivers.driver_dashboard")
        )

    parcel.status = new_status

    try:

        db.session.commit()

        flash(
            f"{parcel.tracking_number} updated to {new_status}.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "DRIVER STATUS ERROR:",
            e
        )

        flash(
            "Unable to update parcel status.",
            "danger"
        )

    return redirect(
        url_for("drivers.driver_dashboard")
    )


# =========================================================
# ASSIGN DRIVER
# =========================================================

@drivers.route(
    "/manage-parcels/<int:parcel_id>/assign-driver",
    methods=["POST"]
)
@login_required
def assign_driver(parcel_id):

    if not staff_or_admin_required():

        flash(
            "You are not authorized to assign drivers.",
            "danger"
        )

        return redirect(
            url_for("parcels.manage_parcels")
        )

    parcel = Parcel.query.get_or_404(parcel_id)

    driver_id = request.form.get(
        "driver_id",
        ""
    ).strip()

    if not driver_id:

        parcel.assigned_driver_id = None

        try:

            db.session.commit()

            flash(
                "Driver assignment removed.",
                "success"
            )

        except Exception as e:

            db.session.rollback()

            print(
                "REMOVE DRIVER ERROR:",
                e
            )

            flash(
                "Unable to remove driver assignment.",
                "danger"
            )

        return redirect(
            url_for("parcels.manage_parcels")
        )

    try:

        driver_id = int(driver_id)

    except ValueError:

        flash(
            "Invalid driver selected.",
            "danger"
        )

        return redirect(
            url_for("parcels.manage_parcels")
        )

    driver = User.query.filter_by(
        id=driver_id,
        role="Driver",
        status=True
    ).first()

    if not driver:

        flash(
            "Selected driver does not exist or is inactive.",
            "danger"
        )

        return redirect(
            url_for("parcels.manage_parcels")
        )

    parcel.assigned_driver_id = driver.id

    if parcel.status == "Pending":
        parcel.status = "Received"

    try:

        db.session.commit()

        flash(
            f"Parcel {parcel.tracking_number} assigned to {driver.name}.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "ASSIGN DRIVER ERROR:",
            e
        )

        flash(
            "Unable to assign driver.",
            "danger"
        )

    return redirect(
        url_for("parcels.manage_parcels")
    )
