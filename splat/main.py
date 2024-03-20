try:
    from splat.crawler import *
    from splat.renderer import *
    from splat.random_wp import *
except:
    from crawler import *
    from renderer import *
    from random_wp import *


class SplatBot():
    def __init__(self, URL):
        global images
        self.images = URL +"/splat/images/"
        self.data = URL + "/splat/data/"
        self.URL = URL + "/splat/"
    
    def get_regular(self,tz = "东部"):
        update()
        li = parse_regular(tz)[:5*2]
        return render_battle(li, tz,"占地模式",self.images)

    def get_challenge(self, tz = "东部"):
        update()
        li = parse_challenge(tz)[:5*2]
        return render_zg(li, tz,"真格挑战", self.images)

    def get_open(self, tz = "东部"):
        update()
        li = parse_open(tz)[:5*2]
        return render_zg(li, tz,"真格开放",self.images)

    def get_coop(self, tz:str = "东部"):
        update()
        li = parse_coop(tz)
        return render_coop(li, tz,self.images)

    def get_x(self,tz = "东部"):
        update()
        li = parse_x(tz)[:5*2]
        return render_zg(li, tz, "X比赛",self.images)


    def get_random(self, arg):
        li = init_random(self.data,arg)
        return render_random(li,self.images)
    
    def get_event(self, tz = "东部"):
        li = parse_event(tz, self.URL)
        if type(li) == str:
            return li
        else:
            print(li)
            return li
            return render_event(li, tz, "活动比赛",self.images)


