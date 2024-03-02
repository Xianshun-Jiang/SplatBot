from splat.crawler import *
from splat.renderer import *


def get_regular():
    update()
    li = parse_regular()#[:5*2]
    return render_battle(li)

def get_challenge():
    update()
    li = parse_challenge()#[:5*2]
    return render_zg(li)

def get_open():
    update()
    li = parse_open()#[:5*2]
    return render_zg(li)

def get_coop():
    update()
    li = parse_coop()
    return render_coop(li)

def get_x():
    update()
    li = parse_x()#[:5*2]
    return render_zg(li)


