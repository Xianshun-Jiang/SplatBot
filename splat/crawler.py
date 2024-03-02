import requests
import json
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO




# Default settings
url = "https://splatoon3.ink/data/schedules.json"
try:
    f = open('./splat/zh-CN.json',encoding="utf8")
except:
    f = open('./zh-CN.json',encoding="utf8")
dic = json.load(f)

# Get data from database
r = requests.get(url).json()["data"]

# Split data into categories
regular = r["regularSchedules"]['nodes']
ranked = r["bankaraSchedules"]['nodes']
x = r["xSchedules"]['nodes']
coop = r['coopGroupingSchedule']['regularSchedules']['nodes']

event = r['eventSchedules']['nodes']
fest = r['festSchedules']['nodes']

def update():
    # Get the current time
    now = datetime.now()

    # Check if it's exactly on the hour
    if now.minute == 0 and now.second == 0:
        # Get data from database
        r = requests.get(url).json()["data"]

        # Split data into categories
        regular = r["regularSchedules"]['nodes']
        ranked = r["bankaraSchedules"]['nodes']
        x = r["xSchedules"]['nodes']
        coop = r['coopGroupingSchedule']['regularSchedules']['nodes']
        event = r['eventSchedules']['nodes']
        fest = r['festSchedules']['nodes']

def translate_stage(id):
    return dic['stages'][id]['name']

def translate_weapon(id):
    return dic['weapons'][id]['name']

def translate_boss(id):
    return dic['bosses'][id]['name']

def translate_rule(id):
    return dic['rules'][id]['name']

def timezone_conversion(time_str):
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    tokyo_datetime = datetime.fromisoformat(time_str).astimezone(tokyo_timezone)

    re = pytz.timezone('America/New_York')
    re = tokyo_datetime.astimezone(re)
    return re.strftime('%m-%d %H:%M')

def parse_regular():
    stages = []

    for item in regular:
        # Get all necessary data

        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime'])
        for vs_stage in item["regularMatchSetting"]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img =vs_stage['image']['url']

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img})
            stages.append(tmp)

    return stages

def parse_challenge():
    stages = []

    for item in ranked:
        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime'])
        # Rule
        rule = translate_rule(item["bankaraMatchSettings"][0]["vsRule"]['id'])
        for vs_stage in item["bankaraMatchSettings"][0]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img = vs_stage['image']['url']

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img, "rule":rule})
            stages.append(tmp)

    return stages

def parse_open():
    stages = []

    for item in ranked:
        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime'])
        # Rule
        rule = translate_rule(item["bankaraMatchSettings"][1]["vsRule"]['id'])
        for vs_stage in item["bankaraMatchSettings"][1]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img = vs_stage['image']['url']

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img,'rule':rule})
            stages.append(tmp)

    return stages

def parse_x():
    stages = []

    for item in x:
        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime'])
        # Rule
        rule = translate_rule(item["xMatchSetting"]["vsRule"]['id'])
        for vs_stage in item["xMatchSetting"]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img =vs_stage['image']['url']

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img, 'rule':rule})
            stages.append(tmp)

    return stages

def parse_coop():
    stages = []
    for idx, item in enumerate(coop):
        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime']) 
        # Remaining time
        if idx ==0:
            remain = datetime.now() - datetime.strptime(start,'%m-%d %H:%M')
            # remain = remain.strftime('%m-%d %H:%M')
        else:
            remain = 0
        # English name of the boss
        boss_en = item['setting']['boss']['name']
        # Chinese name of the boss
        boss_cn = translate_boss(item['setting']['boss']['id'])
        # url of the stage
        img = item['setting']['coopStage']['thumbnailImage']['url']
        # All weapons

        weapons_name = []
        for wp in item['setting']['weapons']:
            weapons_name.append(wp['name'])
        tmp = dict({'start':start, 'end': end, 'remain':remain,'name_cn':boss_cn, 'name_en':boss_en,'img':img, 'weapons_name':weapons_name })
        stages.append(tmp)
    return stages
        
