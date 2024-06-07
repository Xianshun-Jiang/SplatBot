try:
    from recruitmentScheduler.mongoRouter  import *
    # from  recruitmentScheduler.redisRouter import *
except:
    import mongoRouter
    # import redisRouter

from datetime import timedelta
import re
from collections import defaultdict



class scheduler(object):
    def __init__(self, group = []):
        # self.redis = redisRouter()
        self.mongo = mongoRouter()
        self.group = group

    #公开
    #成功返回0
    # def initiate(self, group = "", groups = "", public = True, owner = "",
    #            kind = "", topic = "", time = "", goal = "",  requirement = ""):
    def initiate(self, group = "", groups = "", public = True, owner = "", lock = False,
               kind = "", topic = "", time = "", goal = "",  requirement = "", open = True, player= "", cancle = False, wanche = False):
            #    lock = False
            #    open = True
        return self.mongo.initiate(group,groups, public, owner, lock, kind, topic, time, goal, requirement, open, player, cancle, wanche)

    #不公开募集
    # def private_initiate()

    #查看可加入车队
    #成功返回0
    def find_available(self, kind = "", group = ""):
        return self.mongo.find_available(kind, group)

    #加入车队
    #成功返回0
    def join(self, kind = "", group = "", num = "", player = "", wxid = ""):
        return self.mongo.join(kind, group, num, player, wxid)

    #离开车队
    #成功返回0
    def leave(self, kind = "", group = "", num = "", player = "", wxid = ""):
        return self.mongo.leave(kind, group, num, player, wxid)

    #锁车（只有车主有权限）
    #成功返回0
    def lock(self, kind = "", group = "", owner = "", num = ""):
        return self.mongo.lock(kind, group, owner, num)
    
    #解锁车（只有车主有权限）
    #成功返回0
    def unlock(self, kind = "", group = "", owner = "", num = ""):
        return self.mongo.unlock(kind, group, owner, num)

    #关闭车（车队不可见且操作不可逆,只有车主有权限）
    #成功返回0
    def close(self, kind = "", group = "", owner = "", num = ""):
        return self.mongo.close(kind, group, owner, num)

    #查看车队 (仅开放状态可见)
    def find_by_num(self, kind = "", num = ""):
        return self.mongo.find_by_num(kind, num)
    
    #取消募集
    def cancle(self, kind = "", group = "", owner = "", num = ""):
        return self.mongo.cancle(kind, group, owner, num)
    
    #完车 募集
    def wanche(self, kind = "", group = "", owner = "", num = ""):
        return self.mongo.wanche(kind, group, owner, num)