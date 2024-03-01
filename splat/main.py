from splat.crawler import *
from splat.renderer import *


def get_regular():
    li = parse_regular()
    return render_battle(li)

def get_challenge():
    li = parse_challenge()
    return render_battle(li)

def get_open():
    li = parse_open()
    return render_battle(li)

def get_coop():
    li = parse_coop()
    return render_coop(li)

def get_x():
    li = parse_x()
    return render_battle(li)

