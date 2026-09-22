from datetime import datetime

from APP.extensions import db


class Parcel(db.Model):
    __tablename__ = "parcels"

    id = db.Column(db.Integer, primary_key=True)

    tracking_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    assigned_driver_id = db.Column(
    db.Integer,
    db.ForeignKey("users.id"),
    nullable=True
    )

    parcel_description = db.Column(
        db.String(255),
        nullable=False
    )

    pickup_address = db.Column(
        db.String(255),
        nullable=False
    )

    pickup_latitude = db.Column(
        db.Float,
        nullable=True
    )

    pickup_longitude = db.Column(
        db.Float,
        nullable=True
    )

    destination_address = db.Column(
        db.String(255),
        nullable=False
    )

    destination_latitude = db.Column(
        db.Float,
        nullable=True
    )

    destination_longitude = db.Column(
        db.Float,
        nullable=True
    )

    pickup_date = db.Column(
        db.Date,
        nullable=True
    )

    pickup_time = db.Column(
        db.Time,
        nullable=True
    )

    # ========================================================
    # PARCEL STATUS
    # ========================================================

    status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    # ========================================================
    # PAYMENT INFORMATION
    # ========================================================

    delivery_charge = db.Column(
        db.Numeric(10, 2),
        default=0.00,
        nullable=False
    )

    payment_status = db.Column(
        db.String(30),
        default="Pending",
        nullable=False
    )

    payment_method = db.Column(
        db.String(30),
        nullable=True
    )

    payment_reference = db.Column(
        db.String(100),
        nullable=True
    )

    payment_date = db.Column(
        db.DateTime,
        nullable=True
    )

    # ========================================================
    # TIMESTAMPS
    # ========================================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )