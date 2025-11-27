import requests

def get_location():
    res = requests.get("https://ipinfo.io/json")
    data = res.json()
    lat, lon = map(float, data["loc"].split(","))
    return lon, lat