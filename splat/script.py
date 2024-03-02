import requests

url = "https://splatoon3.ink/data/stages.json"
# Get data from database
r = requests.get(url).json()["data"]['stageRecords']['nodes']

# TODO download images
# print(r)
for it in r:
    name = it['name']
    
    print(it)