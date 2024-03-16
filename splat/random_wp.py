import json
import random
rules = ["真格区域", "真格塔楼", "真格蛤蜊", "真格鱼虎对战"]

def get_random(folder = "", arg= None):
    re = {}
    with open(folder+ "weapons_data.json") as file:
        wp = json.load(file)

    with open(folder + "stage_data.json") as file:
        stages = json.load(file)

    wps = []

    for i in range(8):
        _wp  = random.choice(wp)
        wps.append(_wp)

    re['weapons'] = wps
    re['rule'] = random.choice(rules)
    re['stage'] = random.choice(stages)

    return re
