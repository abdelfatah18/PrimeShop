import requests
from django.conf import settings

PAYMOB_BASE = "https://accept.paymobsolutions.com/api"


# =========================
# Check settings
# =========================
def _ensure_settings():
    missing = []
    if not getattr(settings, "PAYMOB_API_KEY", None):
        missing.append("PAYMOB_API_KEY")
    if not getattr(settings, "PAYMOB_INTEGRATION_ID", None):
        missing.append("INTEGRATION_ID")
    if not getattr(settings, "IFRAME_ID", None):
        missing.append("IFRAME_ID")
    if missing:
        raise RuntimeError(f"Missing PayMob settings: {', '.join(missing)}")


# =========================
# 1️⃣ Authentication
# =========================
def authenticate():
    _ensure_settings()

    url = f"{PAYMOB_BASE}/api/auth/tokens"
    payload = {"api_key": settings.PAYMOB_API_KEY}

    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()

    token = resp.json().get("token")
    if not token:
        raise RuntimeError("PayMob authenticate: token not returned")

    return token


# =========================
# 2️⃣ Create Order (EGP)
# =========================
def create_order(auth_token, order_id, total_amount):
    """
    total_amount = السعر بالجنيه (مثال: 150.75)
    """

    url = f"{PAYMOB_BASE}/ecommerce/orders"

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "merchant_order_id": str(order_id),
        "amount_cents": int(total_amount * 100),  # جنيه → قرش
        "currency": "EGP",
        "delivery_needed": False,
        "items": []  # فاضي (أفضل وأسرع)
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


# =========================
# 3️⃣ Generate Payment Key
# =========================
def generate_payment_key(auth_token, order_id, total_amount, email,
                         billing_data=None, expiration=3600):

    _ensure_settings()

    url = f"{PAYMOB_BASE}/api/acceptance/payment_keys"

    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    default_billing = {
        "apartment": "NA",
        "email": email,
        "floor": "NA",
        "first_name": "Customer",
        "street": "NA",
        "building": "NA",
        "phone_number": "+201000000000",
        "shipping_method": "PKG",
        "postal_code": "00000",
        "city": "Cairo",
        "country": "EG",
        "last_name": "Customer",
        "state": "Cairo"
    }

    if billing_data:
        default_billing.update(billing_data)

    payload = {
        "auth_token": auth_token,
        "amount_cents": int(total_amount * 100),
        "expiration": expiration,
        "order_id": order_id,
        "billing_data": default_billing,
        "currency": "EGP",
        "integration_id": int(settings.PAYMOB_INTEGRATION_ID),
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()

    token = resp.json().get("token")
    if not token:
        raise RuntimeError("PayMob payment key not returned")

    return token
