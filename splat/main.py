from splat.crawler import *
from splat.renderer import *


def get_regular(tz = "东部"):
    update()
    li = parse_regular(tz)#[:5*2]
    return render_battle(li, tz)

def get_challenge(tz = "东部"):
    update()
    li = parse_challenge(tz)[:5*2]
    return render_zg(li, tz)

def get_open(tz = "东部"):
    update()
    li = parse_open(tz)[:5*2]
    return render_zg(li, tz,"真格开放")

def get_coop(tz = "东部"):
    update()
    li = parse_coop(tz)
    return render_coop(li, tz)

def get_x(tz = "东部"):
    update()
    li = parse_x(tz)#[:5*2]
    return render_zg(li, tz)


