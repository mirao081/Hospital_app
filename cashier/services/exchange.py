import requests
from django.conf import settings
from cashier.models import Currency

# Example with Open Exchange Rates (https://openexchangerates.org/)
# Sign up free to get an API key
OXR_API_URL = "https://openexchangerates.org/api/latest.json"

def fetch_exchange_rates():
    api_key = getattr(settings, "OXR_API_KEY", None)
    if not api_key:
        raise ValueError("Open Exchange Rates API key not set in settings.")

    base_currency = Currency.objects.filter(is_base=True).first()
    if not base_currency:
        raise ValueError("No base currency defined.")

    response = requests.get(OXR_API_URL, params={"app_id": api_key, "base": base_currency.code})
    data = response.json()

    if "rates" not in data:
        raise ValueError("Invalid response from API")

    # Update all currencies except base
    for c in Currency.objects.exclude(is_base=True):
        if c.code in data["rates"]:
            c.exchange_rate = data["rates"][c.code]
            c.save(update_fields=["exchange_rate"])
