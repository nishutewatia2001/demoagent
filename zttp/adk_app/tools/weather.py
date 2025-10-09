"""Weather forecast helper using the Open-Meteo public API."""

from __future__ import annotations

from typing import Any, Dict

import requests


def weather_forecast(lat: float, lon: float, date_iso: str) -> Dict[str, Any]:
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "timezone": "auto",
            "start_date": date_iso,
            "end_date": date_iso,
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json().get("daily", {})

