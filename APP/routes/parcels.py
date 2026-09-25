from datetime import datetime
import random

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user

from APP.extensions import db
from APP.models.parcel import Parcel
from APP.models.user import User


# ============================================================
# BLUEPRINT
# ============================================================

parcels = Blueprint("parcels", __name__)


# ============================================================
# STAFF / ADMIN ACCESS
# ============================================================

def staff_or_admin_required():

    return (
        current_user.is_authenticated
        and current_user.role in ["Admin", "Staff"]
    )


# ============================================================
# TRACKING NUMBER
# ============================================================

def generate_tracking_number():

    while True:

        number = random.randint(100000, 999999)

        tracking = f"PD{number}"

        existing = Parcel.query.filter_by(
            tracking_number=tracking
        ).first()

        if not existing:
            return tracking



@parcels.route("/book", methods=["GET", "POST"])
def book_parcel():

    # ============================================================
    # POST - PROCESS BOOKING
    # ============================================================

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone = request.form.get("phone", "").strip()

        parcel_description = request.form.get(
            "parcel_description",
            ""
        ).strip()

        parcel_type = request.form.get(
            "parcel_type",
            ""
        ).strip()

        pickup_address = request.form.get(
            "pickup_address",
            ""
        ).strip()

        destination_address = request.form.get(
            "destination_address",
            ""
        ).strip()

        pickup_date = request.form.get(
            "pickup_date",
            ""
        ).strip()

        pickup_time = request.form.get(
            "pickup_time",
            ""
        ).strip()

        delivery_charge = request.form.get(
            "delivery_charge",
            ""
        ).strip()

        # ========================================================
        # VALIDATION
        # ========================================================

        if not name or not email or not phone:
            flash(
                "Customer name, email and phone are required.",
                "danger"
            )
            return redirect(url_for("parcels.book_parcel"))

        if not parcel_description:
            flash(
                "Please enter a parcel description.",
                "danger"
            )
            return redirect(url_for("parcels.book_parcel"))

        if not pickup_address or not destination_address:
            flash(
                "Pickup and destination addresses are required.",
                "danger"
            )
            return redirect(url_for("parcels.book_parcel"))

        # ========================================================
        # DATE / TIME
        # ========================================================

        pickup_datetime = None

        if pickup_date and pickup_time:

            try:

                pickup_datetime = datetime.strptime(
                    f"{pickup_date} {pickup_time}",
                    "%Y-%m-%d %H:%M"
                )

            except ValueError:

                flash(
                    "Invalid pickup date or time.",
                    "danger"
                )

                return redirect(
                    url_for("parcels.book_parcel")
                )

        # ========================================================
        # DELIVERY CHARGE
        # ========================================================

        try:

            charge = float(delivery_charge or 0)

            if charge < 0:
                raise ValueError

        except ValueError:

            flash(
                "Please enter a valid delivery charge.",
                "danger"
            )

            return redirect(
                url_for("parcels.book_parcel")
            )

        # ========================================================
        # FIND OR CREATE CUSTOMER
        # ========================================================

        customer = User.query.filter(
            db.func.lower(User.email) == email
        ).first()

        if not customer:

            temporary_password = (
                "Customer@123"
            )

            customer = User(
                name=name,
                email=email,
                phone=phone,
                role="Customer",
                status=True
            )

            customer.set_password(
                temporary_password
            )

            db.session.add(customer)

            try:

                db.session.flush()

            except Exception as e:

                db.session.rollback()

                print(
                    "CUSTOMER CREATION ERROR:",
                    type(e).__name__,
                    str(e)
                )

                flash(
                    "Unable to create customer account.",
                    "danger"
                )

                return redirect(
                    url_for("parcels.book_parcel")
                )

        else:

            customer.name = name
            customer.phone = phone

        # ========================================================
        # GENERATE TRACKING NUMBER
        # ========================================================

        tracking_number = generate_tracking_number()

        # ========================================================
        # CREATE PARCEL
        # ========================================================

        parcel = Parcel(

            tracking_number=tracking_number,

            customer_id=customer.id,

            parcel_description=parcel_description,

            pickup_address=pickup_address,

            destination_address=destination_address,

            pickup_date=pickup_datetime,

            status="Pending",

            delivery_charge=charge,

            payment_status="Pending"
        )

        # ========================================================
        # SAVE BOOKING
        # ========================================================

        try:

            db.session.add(parcel)

            db.session.commit()

            print("====================================")
            print("BOOKING SUCCESS")
            print("PARCEL ID:", parcel.id)
            print("TRACKING:", parcel.tracking_number)

            print(
                "PAYMENT URL:",
                url_for(
                    "parcels.parcel_payment",
                    parcel_id=parcel.id
                )
            )

            print("====================================")

        except Exception as e:

            db.session.rollback()

            print(
                "PARCEL BOOKING ERROR:",
                type(e).__name__,
                str(e)
            )

            flash(
                "There was a problem saving the parcel booking.",
                "danger"
            )

            return redirect(
                url_for("parcels.book_parcel")
            )

        # ========================================================
        # SEND CUSTOMER TO PAYMENT
        # ========================================================

        return redirect(
            url_for(
                "parcels.parcel_payment",
                parcel_id=parcel.id
            )
        )

    # ============================================================
    # GET - DISPLAY BOOKING PAGE
    # ============================================================

    return render_template(
        "booking.html"
    )



   
   

    # --------------------------------------------------------
    # CUSTOMER DETAILS
    # --------------------------------------------------------

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    # --------------------------------------------------------
    # PARCEL DETAILS
    # --------------------------------------------------------

    parcel_description = request.form.get(
        "parcel_description",
        ""
    ).strip()

    parcel_type = request.form.get(
        "parcel_type",
        ""
    ).strip()

    pickup_address = request.form.get(
        "pickup_address",
        ""
    ).strip()

    destination_address = request.form.get(
        "destination_address",
        ""
    ).strip()

    pickup_date = request.form.get(
        "pickup_date",
        ""
    ).strip()

    pickup_time = request.form.get(
        "pickup_time",
        ""
    ).strip()

    # --------------------------------------------------------
    # DELIVERY CHARGE
    # --------------------------------------------------------

    delivery_charge_raw = request.form.get(
        "delivery_charge",
        ""
    ).strip()

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not name or not email or not phone:

        flash(
            "Please fill in all customer details.",
            "danger"
        )

        return redirect(
            url_for("parcels.book_parcel")
        )

    if not parcel_description:

        flash(
            "Please enter the parcel description.",
            "danger"
        )

        return redirect(
            url_for("parcels.book_parcel")
        )

    if not parcel_type:

        flash(
            "Please select the parcel type.",
            "danger"
        )

        return redirect(
            url_for("parcels.book_parcel")
        )

    if not pickup_address or not destination_address:

        flash(
            "Please enter pickup and destination locations.",
            "danger"
        )

        return redirect(
            url_for("parcels.book_parcel")
        )

    # --------------------------------------------------------
    # DATE
    # --------------------------------------------------------

    date_value = None

    if pickup_date:

        try:

            date_value = datetime.strptime(
                pickup_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Invalid pickup date.",
                "danger"
            )

            return redirect(
                url_for("parcels.book_parcel")
            )

    # --------------------------------------------------------
    # TIME
    # --------------------------------------------------------

    time_value = None

    if pickup_time:

        try:

            time_value = datetime.strptime(
                pickup_time,
                "%H:%M"
            ).time()

        except ValueError:

            flash(
                "Invalid pickup time.",
                "danger"
            )

            return redirect(
                url_for("parcels.book_parcel")
            )

    # --------------------------------------------------------
    # DELIVERY CHARGE
    # --------------------------------------------------------

    try:

        delivery_charge = float(
            delivery_charge_raw
        )

        if delivery_charge < 0:

            raise ValueError

    except (ValueError, TypeError):

        flash(
            "Please enter a valid delivery charge.",
            "danger"
        )

        return redirect(
            url_for("parcels.book_parcel")
        )

    # --------------------------------------------------------
    # FIND EXISTING CUSTOMER
    # --------------------------------------------------------

    customer = User.query.filter(
        db.func.lower(User.email) == email
    ).first()

    # --------------------------------------------------------
    # CREATE CUSTOMER
    # --------------------------------------------------------

    if not customer:

        try:

            customer = User(
                name=name,
                email=email,
                phone=phone,
                password="temporary",
                role="Customer",
                status=True
            )

            customer.set_password(
                "temporary"
            )

            db.session.add(customer)

            db.session.flush()

        except Exception as e:

            db.session.rollback()

            print(
                "CUSTOMER CREATION ERROR:",
                type(e).__name__,
                str(e)
            )

            # Check whether the customer already exists.
            customer = User.query.filter(
                db.func.lower(User.email) == email
            ).first()

            if not customer:

                flash(
                    "Unable to create the customer account.",
                    "danger"
                )

                return redirect(
                    url_for("parcels.book_parcel")
                )

    else:

        # Update contact details if the customer already exists.
        customer.name = name
        customer.phone = phone

    # --------------------------------------------------------
    # GENERATE TRACKING NUMBER
    # --------------------------------------------------------

    tracking_number = generate_tracking_number()

    # --------------------------------------------------------
    # CREATE PARCEL
    # --------------------------------------------------------

    parcel = Parcel(

        tracking_number=tracking_number,

        customer_id=customer.id,

        parcel_description=parcel_description,

        pickup_address=pickup_address,

        destination_address=destination_address,

        pickup_date=date_value,

        pickup_time=time_value,

        status="Pending",

        delivery_charge=delivery_charge,

        payment_status="Pending"

    )

# ============================================================
# SAVE BOOKING
# ============================================================

    try:

        db.session.add(parcel)

        db.session.commit()

        print("====================================")
        print("BOOKING SUCCESS")
        print("PARCEL ID:", parcel.id)
        print("TRACKING:", parcel.tracking_number)

        print(
            "PAYMENT URL:",
            url_for(
                "parcels.parcel_payment",
                parcel_id=parcel.id
            )
        )

        print("====================================")

    except Exception as e:

        db.session.rollback()

        print(
            "PARCEL BOOKING ERROR:",
            type(e).__name__,
            str(e)
        )

        flash(
            "There was a problem saving the parcel booking.",
            "danger"
        )

        return redirect(
            url_for("parcels.book_parcel")
        )

    # ========================================================
    # SEND CUSTOMER DIRECTLY TO PAYMENT
    # ========================================================

    return redirect(
        url_for(
            "parcels.parcel_payment",
            parcel_id=parcel.id
        )
    )


    
        

    # --------------------------------------------------------
    # SEND CUSTOMER DIRECTLY TO PAYMENT
    # --------------------------------------------------------

    return redirect(
        url_for(
            "parcels.parcel_payment",
            parcel_id=parcel.id
        )
    )


# ============================================================
# TRACK PARCEL
# ============================================================

@parcels.route(
    "/track",
    methods=["GET", "POST"]
)
def track_parcel():

    parcel = None
    searched = False

    if request.method == "POST":

        tracking_number = request.form.get(
            "tracking_number",
            ""
        ).strip().upper()

        searched = True

        if tracking_number:

            parcel = Parcel.query.filter_by(
                tracking_number=tracking_number
            ).first()

    return render_template(
        "tracking.html",
        parcel=parcel,
        searched=searched
    )


# ============================================================
# CUSTOMER DASHBOARD
# ============================================================

@parcels.route("/customer-dashboard")
@login_required
def customer_dashboard():
    if current_user.role != "Customer":
        return redirect(url_for("home"))
    
    # Get customer's parcels
    my_parcels = Parcel.query.filter_by(customer_id=current_user.id).all()
    
    return render_template(
        "customer_dashboard.html",
        parcels=my_parcels,
        user=current_user
    )


# ============================================================
# CUSTOMER PARCEL DETAILS
# ============================================================

@parcels.route(
    "/customer-parcel/<int:parcel_id>"
)
@login_required
def customer_parcel_details(parcel_id):

    if current_user.role != "Customer":

        flash(
            "You do not have permission to access this page.",
            "danger"
        )

        if current_user.role in ["Admin", "Staff"]:

            return redirect(
                url_for("parcels.manage_parcels")
            )

        return redirect(
            url_for("parcels.track_parcel")
        )

    parcel = Parcel.query.get_or_404(
        parcel_id
    )

    if parcel.customer_id != current_user.id:

        flash(
            "You do not have permission to view this parcel.",
            "danger"
        )

        return redirect(
            url_for("parcels.customer_dashboard")
        )

    statuses = [
        "Pending",
        "Received",
        "In Transit",
        "Out for Delivery",
        "Delivered"
    ]

    current_status_index = (
        statuses.index(parcel.status)
        if parcel.status in statuses
        else 0
    )

    return render_template(
        "customers_parcel_details.html",
        parcel=parcel,
        statuses=statuses,
        current_status_index=current_status_index
    )


# ============================================================
# PARCEL MANAGEMENT
# ============================================================

@parcels.route("/manage-parcels")
@login_required
def manage_parcels():

    if not staff_or_admin_required():

        flash(
            "You are not authorized to manage parcels.",
            "danger"
        )

        return redirect(
            url_for("parcels.track_parcel")
        )

    parcels_list = Parcel.query.order_by(
        Parcel.created_at.desc()
    ).all()

    drivers = User.query.filter_by(
        role="Driver",
        status=True
    ).order_by(
        User.name.asc()
    ).all()

    return render_template(
        "manage-parcels.html",
        parcels=parcels_list,
        drivers=drivers
    )


# ============================================================
# UPDATE PARCEL STATUS
# ============================================================

@parcels.route(
    "/manage-parcels/<int:parcel_id>/status",
    methods=["POST"]
)
@login_required
def update_parcel_status(parcel_id):

    if not staff_or_admin_required():

        flash(
            "You are not authorized to update parcel status.",
            "danger"
        )

        return redirect(
            url_for("parcels.track_parcel")
        )

    parcel = Parcel.query.get_or_404(
        parcel_id
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
            "Invalid parcel status.",
            "danger"
        )

        return redirect(
            url_for("parcels.manage_parcels")
        )

    parcel.status = new_status

    try:

        db.session.commit()

        flash(
            f"Parcel {parcel.tracking_number} status updated to {new_status}.",
            "success"
        )

    except Exception as e:

        db.session.rollback()

        print(
            "STATUS UPDATE ERROR:",
            type(e).__name__,
            str(e)
        )

        flash(
            "Unable to update the parcel status.",
            "danger"
        )

    return redirect(
        url_for("parcels.manage_parcels")
    )


# ============================================================
# PAYMENT
# ============================================================

@parcels.route(
    "/payment/<int:parcel_id>",
    methods=["GET", "POST"]
)
def parcel_payment(parcel_id):

    parcel = Parcel.query.get_or_404(
        parcel_id
    )

    # --------------------------------------------------------
    # ALREADY PAID
    # --------------------------------------------------------

    if parcel.payment_status == "Paid":

        return render_template(
            "payment.html",
            parcel=parcel
        )

    # --------------------------------------------------------
    # PROCESS PAYMENT
    # --------------------------------------------------------

    if request.method == "POST":

        payment_method = request.form.get(
            "payment_method",
            ""
        ).strip()

        payment_reference = request.form.get(
            "payment_reference",
            ""
        ).strip()

        allowed_methods = [
            "M-Pesa",
            "Cash",
            "Card",
            "Bank Transfer"
        ]

        # ----------------------------------------------------
        # VALIDATE METHOD
        # ----------------------------------------------------

        if payment_method not in allowed_methods:

            flash(
                "Please select a valid payment method.",
                "danger"
            )

            return redirect(
                url_for(
                    "parcels.parcel_payment",
                    parcel_id=parcel.id
                )
            )

        # ----------------------------------------------------
        # CASH
        # ----------------------------------------------------

        if payment_method == "Cash":

            payment_reference = "CASH"

        # ----------------------------------------------------
        # OTHER METHODS
        # ----------------------------------------------------

        else:

            if not payment_reference:

                flash(
                    "Please enter the payment reference.",
                    "danger"
                )

                return redirect(
                    url_for(
                        "parcels.parcel_payment",
                        parcel_id=parcel.id
                    )
                )

        # ----------------------------------------------------
        # RECORD PAYMENT
        # ----------------------------------------------------

        parcel.payment_method = payment_method

        parcel.payment_reference = payment_reference

        parcel.payment_status = "Paid"

        parcel.payment_date = datetime.utcnow()

        try:

            db.session.commit()

            print("\n====================================")
            print("PAYMENT COMPLETED")
            print("TRACKING:", parcel.tracking_number)
            print("METHOD:", payment_method)
            print("REFERENCE:", payment_reference)
            print("AMOUNT:", parcel.delivery_charge)
            print("====================================\n")

            flash(
                f"Payment for {parcel.tracking_number} recorded successfully.",
                "success"
            )

            return render_template(
                "booking_success.html",
                parcel=parcel
            )

        except Exception as e:

            db.session.rollback()

            print(
                "PAYMENT ERROR:",
                type(e).__name__,
                str(e)
            )

            flash(
                "Unable to record payment.",
                "danger"
            )

            return redirect(
                url_for(
                    "parcels.parcel_payment",
                    parcel_id=parcel.id
                )
            )

    # --------------------------------------------------------
    # DISPLAY PAYMENT PAGE
    # --------------------------------------------------------

    return render_template(
        "payment.html",
        parcel=parcel
    )




