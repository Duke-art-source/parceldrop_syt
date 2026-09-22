from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from APP.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        default="Customer",
        nullable=False
    )

    status = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    # =====================================================
    # CUSTOMER PARCELS
    # =====================================================

    parcels = db.relationship(
        "Parcel",
        foreign_keys="Parcel.customer_id",
        backref="customer",
        lazy=True
    )

    # =====================================================
    # DRIVER PARCELS
    # =====================================================

    driver_parcels = db.relationship(
        "Parcel",
        foreign_keys="Parcel.assigned_driver_id",
        backref="driver",
        lazy=True
    )

    # =====================================================
    # PASSWORD
    # =====================================================

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password,
            password
        )

