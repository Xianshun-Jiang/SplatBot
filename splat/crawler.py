import requests
import json
from datetime import datetime, timezone
import pytz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO



# Default settings
url = "https://splatoon3.ink/data/schedules.json"
trans_url = "https://splatoon3.ink/data/locale/zh-CN.json"
URL = ""

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


def update_trans():
    r = requests.get(trans_url).json()
    with open(URL+'zh-CN.json', 'w', encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
        return r

def update():
    global r, regular,ranked,x,coop,event,fest
    # Get the current time
    # now = datetime.now()

    # Check if it's exactly on the hour
    # if now.minute == 0:
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

def translate(type, id, val):
    global dic
    try:
        tmp = dic[type][id][val]
        return tmp
    except:
        dic = update_trans()
        tmp = dic[type][id][val]
        return tmp


def timezone_conversion(time_str, tz = "东部"):
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    tokyo_datetime = datetime.fromisoformat(time_str).astimezone(tokyo_timezone)
    
    match tz:
        case "东部":
            re = pytz.timezone('America/New_York')
            re = tokyo_datetime.astimezone(re)
            return re
        case "西部":
            re = pytz.timezone('US/Pacific')
            re = tokyo_datetime.astimezone(re)
            return re
        case "中部":
            re = pytz.timezone('US/Central')
            re = tokyo_datetime.astimezone(re)
            return re
        case "山地" | "山区":
            re = pytz.timezone('US/Mountain')
            re = tokyo_datetime.astimezone(re)
            return re

def parse_regular(tz = "东部"):
    stages = []
    global regular

    for idx, item in enumerate(regular):
        # Start time
        start = timezone_conversion(item['startTime'], tz).strftime('%m-%d %H:%M') 
        # End time
        end = timezone_conversion(item['endTime'], tz).strftime('%m-%d %H:%M') 
        # Remaining time
        if idx ==0:
            remain = timezone_conversion(item['endTime'], tz) - datetime.now(timezone.utc) 
        else:
            remain = 0
        try:
            for vs_stage in item["regularMatchSetting"]['vsStages']:
                # Chinese name of the stage
                name_cn = translate_stage(vs_stage["id"])
                # Url of the stage
                img =vs_stage['image']['url']
                img = "./splat/images/stages/"+img.rpartition("/")[-1]


                tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img, 'remain':remain})
                stages.append(tmp)
        except:
            None

    return stages

def parse_challenge(tz = "东部"):
    stages = []
    global ranked

    for idx, item in enumerate(ranked):
        # Start time
        start = timezone_conversion(item['startTime'], tz).strftime('%m-%d %H:%M') 
        # End time
        end = timezone_conversion(item['endTime'], tz).strftime('%m-%d %H:%M') 
        # Remaining time
        if idx == 0:
            remain = timezone_conversion(item['endTime'], tz) - datetime.now(timezone.utc) 
        else:
            remain = 0
        # Rule
        # print(item["bankaraMatchSettings"])
        # print(item["bankaraMatchSettings"][0])
        # print("-----------------------------------")
        try:
            rule = translate_rule(item["bankaraMatchSettings"][0]["vsRule"]['id'])
            for vs_stage in item["bankaraMatchSettings"][0]['vsStages']:
                # Chinese name of the stage
                name_cn = translate_stage(vs_stage["id"])
                # Url of the stage
                img = vs_stage['image']['url']
                img = "./splat/images/stages/"+img.rpartition("/")[-1]


                tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img, "rule":rule, 'remain':remain})
                stages.append(tmp)
        except:
            None

    return stages

def parse_open(tz = "东部"):
    stages = []
    global ranked

    for idx, item in enumerate(ranked):
        # Start time
        start = timezone_conversion(item['startTime'], tz).strftime('%m-%d %H:%M') 
        # End time
        end = timezone_conversion(item['endTime'], tz).strftime('%m-%d %H:%M') 
        # Remaining time
        if idx ==0:
            remain = timezone_conversion(item['endTime'], tz) - datetime.now(timezone.utc) 
        else:
            remain = 0
        try:
            # Rule
            rule = translate_rule(item["bankaraMatchSettings"][1]["vsRule"]['id'])
            for vs_stage in item["bankaraMatchSettings"][1]['vsStages']:
                # Chinese name of the stage
                name_cn = translate_stage(vs_stage["id"])
                # Url of the stage
                img = vs_stage['image']['url']
                img = "./splat/images/stages/"+img.rpartition("/")[-1]

                tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img,'rule':rule, 'remain':remain})
                stages.append(tmp)
        except:
            None

    return stages

def parse_x(tz = "东部"):
    stages = []
    global x

    for idx, item in enumerate(x):
        # Start time
        start = timezone_conversion(item['startTime'], tz).strftime('%m-%d %H:%M') 
        # End time
        end = timezone_conversion(item['endTime'], tz).strftime('%m-%d %H:%M') 
        # Rule
        rule = translate_rule(item["xMatchSetting"]["vsRule"]['id'])
         # Remaining time
        if idx ==0:
            remain = timezone_conversion(item['endTime'], tz) - datetime.now(timezone.utc) 
        else:
            remain = 0
        for vs_stage in item["xMatchSetting"]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img =vs_stage['image']['url']
            img = "./splat/images/stages/"+img.rpartition("/")[-1]

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img, 'rule':rule, 'remain':remain})
            stages.append(tmp)

    return stages

def parse_coop(tz = "东部"):
    stages = []
    global coop
    for idx, item in enumerate(coop):
        # Start time
        start = timezone_conversion(item['startTime'],tz).strftime('%m-%d %H:%M')
        # End time
        end = timezone_conversion(item['endTime'], tz).strftime('%m-%d %H:%M') 
        # Remaining time
        if idx ==0:
            remain = timezone_conversion(item['endTime'], tz) - datetime.now(timezone.utc) 
        else:
            remain = 0
        # English name of the boss
        boss_en = item['setting']['boss']['name']
        # Chinese name of the boss
        boss_cn = translate_boss(item['setting']['boss']['id'])
        # url of the stage
        img = item['setting']['coopStage']['thumbnailImage']['url']
        img = "./splat/images/stages/"+img.rpartition("/")[-1]
        # Stage name
        stage_cn = translate_stage(item['setting']['coopStage']['id'])
        # All weapons
        weapons_name = []
        for wp in item['setting']['weapons']:
            weapons_name.append(wp['name'])

        tmp = dict({'start':start, 'end': end, 'remain':remain,'name_cn':boss_cn, 'name_en':boss_en,'img':img, 'weapons_name':weapons_name, 'stage_cn':stage_cn})
        stages.append(tmp)
    return stages
        
def parse_event(tz = "东部", _URL = ""):
    global dict
    global URL
    URL = _URL
    re = []
    update()
    if len(event) == 0:
        return "目前没有活动比赛"
    for idx, eve in enumerate(event):
        _id = eve["leagueMatchSetting"]["leagueMatchEvent"]['id']
        _name = translate("events", _id, "name")
        _desc = translate("events", _id, "regulation")
        _time = eve['timePeriods']
        _stages = eve["leagueMatchSetting"]["vsStages"]
        tmp = []
        for i in range(len(_stages)):
            __name =  translate("stages", _stages[i]['id'],"name")
            __url =  "./splat/images/stages/"+_stages[i]['image']['url'].rpartition("/")[-1] 
            tmp.append(dict({"name": __name, "url": __url}))
        for i in range(len(_time)):
            _time[i]['startTime'] =  timezone_conversion(_time[i]['startTime'], tz).strftime('%m-%d %H:%M') 
            _time[i]['endTime'] =  timezone_conversion(_time[i]['endTime'], tz).strftime('%m-%d %H:%M') 


        tmp = dict({"name": _name, "stages":tmp,"desc":_desc, "time":_time})
        re.append(tmp)
    return re 