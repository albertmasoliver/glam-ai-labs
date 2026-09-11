"""Weather app -- the DOGHOUSE version.

Type in a city, get current conditions and a short forecast.

This is deliberately a "before" state, with all the usual doghouse problems:

  - everything in one file
  - the network call sits inline in the route handler
  - no input validation
  - no tests, and nothing that could be tested without the network
  - the API key is read at import time
  - error handling leaks implementation details

The lab uses it to draw a trust map. Do not "fix" it before the lab.

Run it:
    pip install -r requirements.txt
    WEATHER_STUB=1 python main.py        # no API key needed
    open http://localhost:5000
"""

import os

import requests
from flask import Flask, render_template, request

app = Flask(__name__)

OWM_API_KEY = os.environ.get("OWM_API_KEY")
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

# When set, serve canned data instead of calling OpenWeather, so the lab runs
# without anyone needing a key. This is a fixture switch, not a seam -- it is
# not a substitute for a client you can hand a fake to.
STUB = os.environ.get("WEATHER_STUB") == "1"

STUB_PAYLOAD = {
    "current": {"temp": 17.4, "weather": [{"description": "scattered clouds"}]},
    "daily": [
        {"dt": 0, "temp": {"min": 12.1, "max": 19.8}, "weather": [{"description": "light rain"}]},
        {"dt": 1, "temp": {"min": 11.7, "max": 21.2}, "weather": [{"description": "clear sky"}]},
        {"dt": 2, "temp": {"min": 13.0, "max": 22.6}, "weather": [{"description": "few clouds"}]},
    ],
}


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        city = request.form.get("city")
        return weather(city)
    return render_template("index.html")


@app.route("/<city>")
def weather(city):
    if STUB:
        return render_template(
            "weather.html", city=city.title(), data=STUB_PAYLOAD
        )

    geo = requests.get(
        GEOCODE_URL,
        params={"q": city, "limit": 1, "appid": OWM_API_KEY},
        timeout=10,
    ).json()

    lat = geo[0]["lat"]
    lon = geo[0]["lon"]

    data = requests.get(
        ONECALL_URL,
        params={
            "lat": lat,
            "lon": lon,
            "exclude": "minutely,hourly,alerts",
            "units": "metric",
            "appid": OWM_API_KEY,
        },
        timeout=10,
    ).json()

    return render_template("weather.html", city=city.title(), data=data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
