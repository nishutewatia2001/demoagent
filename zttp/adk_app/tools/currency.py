"""Currency conversion helper backed by exchangerate.host."""

from __future__ import annotations

from typing import Dict

import requests

BASE_URL = "https://api.exchangerate.host/convert"


def currency_convert(amount: float, from_currency: str, to_currency: str) -> Dict[str, float]:
    response = requests.get(
        BASE_URL,
        params={
            "from": from_currency,
            "to": to_currency,
            "amount": amount,
            "places": 2,
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return {
        "query_amount": amount,
        "from": from_currency,
        "to": to_currency,
        "result": data.get("result", 0.0),
    }

