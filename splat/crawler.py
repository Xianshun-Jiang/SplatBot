import requests
import json
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO




# Default settings
url = "https://splatoon3.ink/data/schedules.json"
f = open('./splat/zh-CN.json',encoding="utf8")
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


def translate_stage(id):
    return dic['stages'][id]['name']

def translate_weapon(id):
    return dic['weapons'][id]['name']

def translate_boss(id):
    return dic['bosses'][id]['name']

def timezone_conversion(time_str):
    tokyo_timezone = pytz.timezone('Asia/Tokyo')
    tokyo_datetime = datetime.fromisoformat(time_str).astimezone(tokyo_timezone)

    re = pytz.timezone('America/New_York')
    re = tokyo_datetime.astimezone(re)
    return re.strftime('%m-%d %H:%M')

def render_battle(li):
    width = 400
    height = 600
    i = 0
    re = Image.new("RGB", (400, 1000), "white")
    tmp  = ImageDraw.Draw(re)
    x = 100
    y = 40
    for idx, item in enumerate(li):
        # print(item)
        start = item['start']
        end = item['end']
        name = item['name_cn']
        url = item['img']
        # Send a GET request to the URL
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Read the content of the response as bytes
            image_bytes = BytesIO(response.content)
            
            # Open the image using Pillow
            image_to_add = Image.open(image_bytes)
            
            # Resize image:

            scale = 0.3
            size = (int(scale * image_to_add.size[0]), int(scale * image_to_add.size[1]))

            image_to_add = image_to_add.resize(size)
            
            # Initialize the drawing context
            # draw = ImageDraw.Draw(re)
            
            # Choose a font and size
            font = ImageFont.truetype("arial.ttf", size=18)
            
            # Specify text position
            text_position = (0, y)
            end_position = (0,y+30)
        
            # Add text to the image
            tmp.text(text_position, start, fill="black", font=font)
            tmp.text(end_position, end, fill="black", font=font)

            position = (x, y)
            x = 340 - x
            #x=100 is the default 
            if x == 100:
                y+= 70

            re.paste( image_to_add,position)
            

            
        else:
            # If the request failed, print an error message
            print(f"Failed to retrieve image from URL: {url}")
            return None
        i = 1 - i
    return re
    
def render_coop(li):
     for item in li:
        print(item)

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
        for vs_stage in item["bankaraMatchSettings"][0]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img = vs_stage['image']['url']

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img})
            stages.append(tmp)

    return stages

def parse_open():
    stages = []

    for item in ranked:
        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime'])
        for vs_stage in item["bankaraMatchSettings"][1]['vsStages']:
            # Chinese name of the stage
            name_cn = translate_stage(vs_stage["id"])
            # Url of the stage
            img = vs_stage['image']['url']

            tmp = dict({'start':start, 'end': end, 'name_cn':name_cn,'img':img})
            stages.append(tmp)

    return stages

def parse_coop():
    stages = []
    for item in coop:
        # Start time
        start = timezone_conversion(item['startTime'])
        # End time
        end = timezone_conversion(item['endTime'])
        # Chinese name of the boss
        boss_cn = translate_boss(item['setting']['boss']['id'])
        # url of the stage
        img = item['setting']['coopStage']['thumbnailImage']['url']
        # All weapons
        weapons = []
        for wp in item['setting']['weapons']:
            weapons.append(wp['image']['url'])
        tmp = dict({'start':start, 'end': end, 'name_cn':boss_cn,'img':img, 'weapons':weapons})
        stages.append(tmp)
    return stages
        
def get_regular():
    return render_battle(parse_regular())

def get_challenge():
    return render_battle(parse_challenge())

def get_open():
    return render_battle(parse_open())

def get_coop():
    return render_coop(parse_coop())

# parse_coop()
# print(parse_])
# get_challenge().show()
