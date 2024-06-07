import pymongo  

class mongoRouter(object):  
    def __init__(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.splatoon_recruitment

    def count(self, li, item):
        re = 0
        for i in li:
            if item == i:
                re+=1
        return re

    # initiate a record
    # return num of the recruitment
    def initiate(self, group = "", groups = "", public = True, owner = "", lock = False,
               kind = "", topic = "", time = "", goal = "",  requirement = "", open = True, player = "",cancle = False, wanche = False):
        # group: where the recruitment initiated
        # groups: groups of the recruitment
        # public: if the recruitment is public
        # owner: who initiate the recruitment
        # lock: if the recruitment is locked
        # kind: the kind of the recruitment (open, work, etc.)
        # topic: the topic of the recruitment
        # time: the time of the recruitment
        # goal: the goal of the recruitment
        # requirement: the requirement of the recruitment
        # open: whether the recruitment is open

        # get the number of all records
        num = len(list(self.db[kind].find({})))
        num = str(num)
        mem = {owner:group}
        # create a record
        record = {"num" : num, "owner" :owner, "group":group, "groups":groups, "lock": lock,"public": public, "topic":topic, 
                    "time":time, "goal":goal, "requirement":requirement, "open":open, "players":[player], 
                    "cancle": cancle, "wanche": wanche, "member_wxid":[mem]}
        
        # insert the record
        self.db[kind].insert_one(record)
        return num
    
    # find all records by kind
    # return a list
    def find_all(self, kind = "", ):
        re = list(self.db[kind].find({}))
        return re
    
    # find all records with the same group that initiated the recruitments
    # return a list
    def find_by_group(self, kind = "", group = ""):
        # find all the records with the same group
        re = list(self.db[group].find({"group":group}))
        return re

    # find all records with the same owner
    # return a list
    def find_by_owner(self, kind = "", owner = ""):
        # find all the records with the same owner
        re = list(self.db[kind].find({"owner":owner}))
        return re

    # find all records that are open    
    # return a list
    def find_available(self, kind = "", group = ""):
        # find all the records that are open and public
        tmp = list(self.db[kind].find({"public":True, "open":True, "cancle":False, "wanche": False}))
        # find all records that are open but not public
        tmp2 = list(self.db[kind].find({"public":False, "open":True, "cancle":False, "wanche": False}))
        tmp2 = [i for i in tmp2 if group in i["groups"]]
        # combine the two lists
        re = tmp + tmp2
        return re
    
    # find a record by num
    # return a record
    def find_by_num(self, kind = "", num = ""):
        re = self.db[kind].find_one({"num":num, "open":True, "cancle":False, "wanche": False})
        return re
    
    # find public and unlocked recruitment
    # return a list
    def find_public_unlocked(self, kind = "", group = ""):
        re = list(self.db[kind].find({"public":True, "lock":False, "open":True,  "cancle":False, "wanche": False}))
        return re
    
    # close a recruitment
    # return 0 if success 1 otherwise
    def close(self, kind = "", group = "", owner = "", num = ""):
        if type(num) == str:
            record = self.find_by_num(group, num)
            if record.get("owner") != owner:
                return 1
            # update the open status of the record
            self.db[kind].update_one({"group":group, "num":num, "owner":owner}, {"$set":{"open":False}})
            return 0
        return 1
    
    # join a recruitment
    # return 0 if success 
    def join(self, kind = "", group = "", num = "", player = "", wxid = ""):
        record = self.find_by_num(kind, num)
        if record is None:
            return 3
        if record.get("lock") == True or record.get("open") == False or record.get("cancle") or record.get("wanche"):
            return 1
        if len(record.get("players")) >= 4:
            return 2
        
        # update the players of the record
        mem = {wxid:group}
        self.db[kind].update_one({"num":num, "open":True, "cancle":False, "wanche": False}, {"$push":{"players":player, "member_wxid":mem}})
        return 0

    # leave a recruitment
    # return 0 if success 1 otherwise
    def leave(self, kind = "", group = "", num = "", player = "", wxid = ""):
        record = self.find_by_num(kind, num)
        if record.get("lock") == True:
            return 1
        if record.get("players")[0] == player:
            return 2
        mem = {wxid:group}
        counter_player = self.count(record.get("players"), player)
        counter_wxid = self.count(record.get("member_wxid"), mem)
        # update the players of the record
        self.db[kind].update_one({"num":num, "open":True, "cancle":False, "wanche": False}, {"$pull":{"players":player}})
        self.db[kind].update_one({"num":num, "open":True, "cancle":False, "wanche": False}, {"$pull":{"member_wxid":mem}})

        for i in range(counter_player - 1):
            self.db[kind].update_one({"num":num, "open":True, "cancle":False, "wanche": False}, {"$push":{"players":player}})
        for i in range(counter_wxid - 1):
            self.db[kind].update_one({"num":num, "open":True, "cancle":False, "wanche": False}, {"$push":{"member_wxid":mem}})
        
        return 0

    # lock a recruitment
    def lock(self, kind = "", group = "", owner = "", num = ""):
        record = self.find_by_num(kind, num)
        if record.get("owner") != owner:
            return 1
        if record.get("cancle"):
            return 2
        if record.get("wanche"):
            return 3
        # update the lock status of the record
        self.db[kind].update_one({"num":num, "owner":owner, "open":True, "cancle":False, "wanche": False}, {"$set":{"lock":True}})
        return 0

    # unlock a recruitment
    def unlock(self, kind = "", group = "", owner = "", num = ""):
        record = self.find_by_num(kind, num)
        if record.get("owner") != owner:
            return 1
        if record.get("cancle"):
            return 2
        if record.get("wanche"):
            return 3
        # update the lock status of the record
        self.db[kind].update_one({"num":num, "owner":owner, "open":True, "cancle":False, "wanche": False}, {"$set":{"lock":False}})
        return 0

    
    # cancle a recruitment
    def cancle(self, kind = "", group = "", owner = "", num = ""):
        record = self.find_by_num(kind, num)
        if record.get("owner") != owner:
            return 1
        # update the cancle status of the record
        self.db[kind].update_one({"num":num, "owner":owner,"open":True, "cancle":False, "wanche": False}, {"$set":{"cancle":True}})
        return 0


    # wanche a recruitment
    def wanche(self, kind = "", group = "", owner = "", num = ""):
        record = self.find_by_num(kind, num)
        if record.get("owner") != owner:
            return 1
        # update the cancle status of the record
        self.db[kind].update_one({"num":num, "owner":owner,"open":True, "cancle":False, "wanche": False}, {"$set":{"wanche":True}})
        return 0

    