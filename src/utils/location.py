import requests

def get_location():
    res = requests.get("https://ipinfo.io/json")
    data = res.json()
    lon, lat = map(float, data["loc"].split(","))
    return (lon, lat)