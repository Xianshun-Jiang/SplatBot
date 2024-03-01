import requests

url = "https://splatoon3.ink/data/schedules.json"
# Get data from database
r = requests.get(url).json()["data"]

# TODO download images