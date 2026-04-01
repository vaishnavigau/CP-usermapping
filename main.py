from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# ✅ CORS (so frontend can call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Convert city → lat/lng
def geocode(location):
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json"
    headers = {"User-Agent": "cp-map-app"}

    res = requests.get(url, headers=headers).json()

    if len(res) == 0:
        return None, None

    return res[0]["lat"], res[0]["lon"]


# 🔹 Single user API
@app.get("/user/{handle}")
def get_user(handle: str):
    url = f"https://codeforces.com/api/user.info?handles={handle}"
    res = requests.get(url).json()

    if res["status"] != "OK":
        return {"error": "User not found"}

    user = res["result"][0]

    city = user.get("city")
    country = user.get("country")

    if not city:
        return {"error": "Location not available"}

    lat, lon = geocode(f"{city}, {country}")

    if not lat:
        return {"error": "Could not fetch coordinates"}

    return {
        "handle": handle,
        "city": city,
        "country": country,
        "lat": lat,
        "lng": lon
    }


# 🔹 Multiple users API
@app.get("/users")
def get_users():
    handles = ["tourist", "Petr", "Benq", "ecnerwala", "Um_nik", "neal"]

    users = []

    for handle in handles:
        url = f"https://codeforces.com/api/user.info?handles={handle}"
        res = requests.get(url).json()

        if res["status"] != "OK":
            continue

        user = res["result"][0]
        city = user.get("city")
        country = user.get("country")

        if not city:
            continue

        lat, lon = geocode(f"{city}, {country}")

        if not lat:
            continue

        users.append({
            "handle": handle,
            "city": city,
            "country": country,
            "lat": lat,
            "lng": lon
        })

    return users