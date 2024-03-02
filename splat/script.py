import requests

url = "https://splatoon3.ink/data/stages.json"
stage_url="https://splatoon3.ink/assets/splatnet/v2/stage_img/icon/low_resolution/"
# Get data from database
r = requests.get(url).json()["data"]['stageRecords']['nodes']



# TODO download images
# print(r)
for it in r:
    name = it['name']
    
    print(it)