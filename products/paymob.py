import requests
from django.conf import settings

# -------------------------
# Helper functions for PayMob
# -------------------------
# تأكد إنك ضايف في settings.py:
# PAYMOB_API_KEY, INTEGRATION_ID, IFRAME_ID
# مثال:
# PAYMOB_API_KEY = "your_api_key"
# INTEGRATION_ID = 123456
# IFRAME_ID = 123456

PAYMOB_BASE = "https://accept.paymobsolutions.com/api"



def _ensure_settings():
    missing = []
    if not getattr(settings, "PAYMOB_API_KEY", None):
        missing.append("PAYMOB_API_KEY")
    if not getattr(settings, "INTEGRATION_ID", None):
        missing.append("INTEGRATION_ID")
    if not getattr(settings, "IFRAME_ID", None):
        missing.append("IFRAME_ID")
    if missing:
        raise RuntimeError(f"Missing PayMob settings: {', '.join(missing)}")


def authenticate():
    """
    يحصل على auth_token من PayMob.
    يعيد الـ auth_token كسلسلة أو يرمي استثناء واضح لو فشل.
    """
    _ensure_settings()
    url = f"{PAYMOB_BASE}/api/auth/tokens"
    payload = {"api_key": settings.PAYMOB_API_KEY}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        # فشل الشبكة أو وقت الاستجابة
        raise RuntimeError(f"PayMob authenticate failed: {e}") from e

    data = resp.json()
    token = data.get("token")
    if not token:
        raise RuntimeError(f"PayMob authenticate: no token in response: {data}")
    return token


def create_order(auth_token, amount_cents, merchant_order_id=None, delivery_needed=False):
    """
    ينشئ Order في PayMob (ecommerce/orders)
    - auth_token: ناتج authenticate()
    - amount_cents: المبلغ بالبس (مثلاً EGP -> جنيه * 100)
    - merchant_order_id: أي قيمة تعريفية عندك (مثلاً Payment.id أو Order.id)
    يعيد dict الاستجابة (json) أو يرمي استثناء.
    """
    url = f"{PAYMOB_BASE}/ecommerce/orders"
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "delivery_needed": delivery_needed,
        "amount_cents": amount_cents,
        "currency": "EGP",
        "merchant_order_id": str(merchant_order_id) if merchant_order_id is not None else None,
        # العناصر (items) اختيارية — تقدر تضيف تفاصيل لو تحب
        "items": [],
    }

    # احذف المفاتيح اللي قيمتها None
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"PayMob create_order failed: {e}") from e

    return resp.json()


def generate_payment_key(auth_token, order_id, amount_cents, email,
                         billing_data=None, expiration=3600, integration_id=None):
    """
    ينشئ payment_key (token) لاستخدامه في iframe.
    - billing_data: dict اختياري لو عندك بيانات العميل (phone, first_name, last_name, city, country,...)
    - integration_id: لو حبيت تجاوزه، يقرأ من settings.INTEGRATION_ID
    يعيد token كسلسلة أو يرمي استثناء.
    """
    _ensure_settings()
    if integration_id is None:
        integration_id = getattr(settings, "INTEGRATION_ID")

    url = f"{PAYMOB_BASE}/api/acceptance/payment_keys"
    headers = {"Authorization": f"Bearer {auth_token}"}

    # بيانات افتراضية قابلة للتبديل (اختبارية)
    default_billing = {
        "apartment": "N/A",
        "email": email or "test@example.com",
        "floor": "N/A",
        "first_name": "Customer",
        "street": "N/A",
        "building": "N/A",
        "phone_number": "+201000000000",  # تأكد من شكل رقم الهاتف
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
        "amount_cents": amount_cents,
        "expiration": expiration,
        "order_id": order_id,
        "billing_data": default_billing,
        "currency": "EGP",
        "integration_id": int(integration_id),
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"PayMob generate_payment_key failed: {e} - response: {getattr(e, 'response', None)}") from e

    data = resp.json()
    token = data.get("token")
    if not token:
        raise RuntimeError(f"PayMob generate_payment_key: no token in response: {data}")
    return token
