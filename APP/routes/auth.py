from urllib.parse import urlparse, urljoin

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from APP.models.user import User


auth = Blueprint("auth", __name__)


# ============================================================
# SAFE NEXT-PAGE HANDLING
# ============================================================

def is_safe_url(target):
    """
    Only allow redirects to URLs on this application.

    This prevents malicious URLs such as:
        /login?next=https://malicious-site.com
    """

    if not target:
        return False

    try:
        target_url = urlparse(
            urljoin(request.host_url, target)
        )

        host_url = urlparse(request.host_url)

        return (
            target_url.scheme in ("http", "https")
            and target_url.netloc == host_url.netloc
        )

    except Exception:
        return False


def get_safe_next_url():
    """
    Return the requested next URL only when it is safe.
    Otherwise return None.
    """

    next_url = request.args.get("next", "").strip()

    if is_safe_url(next_url):
        return next_url

    return None


# ============================================================
# ROLE-BASED DEFAULT REDIRECT
# ============================================================

def get_role_redirect(user):
    """
    Determine the normal landing page for each user role.
    """

    if user.role in ["Admin", "Staff"]:
        return url_for(
            "parcels.manage_parcels"
        )

    if user.role == "Driver":
        return url_for(
            "drivers.driver_dashboard"
        )

    return url_for(
        "parcels.customer_dashboard"
    )


# ============================================================
# LOGIN
# ============================================================

@auth.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # ALREADY LOGGED IN
    # --------------------------------------------------------

    if current_user.is_authenticated:

        return redirect(
            get_role_redirect(current_user)
        )

    # --------------------------------------------------------
    # GET LOGIN PAGE
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "login.html"
        )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    # --------------------------------------------------------
    # SAFE NEXT URL
    #
    # For POST requests, the next value may come from:
    # - the query string
    # - a hidden form field
    # --------------------------------------------------------

    next_url = request.args.get(
        "next",
        ""
    ).strip()

    if not next_url:

        next_url = request.form.get(
            "next",
            ""
        ).strip()

    if not is_safe_url(next_url):

        next_url = None

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not email or not password:

        flash(
            "Please enter your email and password.",
            "danger"
        )

        if next_url:

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        return redirect(
            url_for("auth.login")
        )

    # --------------------------------------------------------
    # FIND USER
    # --------------------------------------------------------

    user = User.query.filter(
        User.email == email
    ).first()

    if not user:

        flash(
            "Invalid email or password.",
            "danger"
        )

        if next_url:

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        return redirect(
            url_for("auth.login")
        )

    # --------------------------------------------------------
    # ACCOUNT STATUS
    # --------------------------------------------------------

    if not user.status:

        flash(
            "Your account is inactive.",
            "danger"
        )

        if next_url:

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        return redirect(
            url_for("auth.login")
        )

    # --------------------------------------------------------
    # PASSWORD
    # --------------------------------------------------------

    if not user.check_password(password):

        flash(
            "Invalid email or password.",
            "danger"
        )

        if next_url:

            return redirect(
                url_for(
                    "auth.login",
                    next=next_url
                )
            )

        return redirect(
            url_for("auth.login")
        )

    # --------------------------------------------------------
    # LOGIN USER
    # --------------------------------------------------------

    login_user(user)

    # --------------------------------------------------------
    # DEBUG INFORMATION
    # --------------------------------------------------------

    print("\n================================")
    print("USER LOGIN SUCCESSFUL")
    print("================================")
    print("USER ID:", user.id)
    print("NAME:", user.name)
    print("EMAIL:", user.email)
    print("ROLE:", user.role)
    print("STATUS:", user.status)
    print("NEXT URL:", next_url)
    print("================================\n")

    # --------------------------------------------------------
    # SAFE NEXT-PAGE REDIRECT
    #
    # Important:
    # The requested page must also be appropriate for the
    # logged-in user's role.
    #
    # A Driver should not be able to use:
    # ?next=/manage-parcels
    #
    # to bypass role restrictions.
    # --------------------------------------------------------

    if next_url:

        if user.role == "Driver":

            driver_url = url_for(
                "drivers.driver_dashboard"
            )

            if next_url == driver_url:
                print(
                    "REDIRECTING DRIVER TO REQUESTED PAGE:",
                    next_url
                )

                return redirect(next_url)

        elif user.role in ["Admin", "Staff"]:

            manage_url = url_for(
                "parcels.manage_parcels"
            )

            if next_url == manage_url:

                print(
                    "REDIRECTING ADMIN/STAFF TO REQUESTED PAGE:",
                    next_url
                )

                return redirect(next_url)

        else:

            customer_url = url_for(
                "parcels.customer_dashboard"
            )

            if next_url == customer_url:

                print(
                    "REDIRECTING CUSTOMER TO REQUESTED PAGE:",
                    next_url
                )

                return redirect(next_url)

    # --------------------------------------------------------
    # ROLE-BASED DEFAULT REDIRECT
    # --------------------------------------------------------

    if user.role == "Driver":

        print(
            "REDIRECTING DRIVER TO DASHBOARD"
        )

        return redirect(
            url_for(
                "drivers.driver_dashboard"
            )
        )

    # --------------------------------------------------------
    # ADMIN / STAFF
    # --------------------------------------------------------

    if user.role in ["Admin", "Staff"]:

        print(
            "REDIRECTING ADMIN/STAFF TO MANAGE PARCELS"
        )

        return redirect(
            url_for(
                "parcels.manage_parcels"
            )
        )

    # --------------------------------------------------------
    # CUSTOMER
    # --------------------------------------------------------

    print(
        "REDIRECTING CUSTOMER TO CUSTOMER DASHBOARD"
    )

    return redirect(
        url_for(
            "parcels.customer_dashboard"
        )
    )


# ============================================================
# LOGOUT
# ============================================================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )

