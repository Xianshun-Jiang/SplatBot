import pymongo  

class mongoRouter(object):  
    def __init__(self):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.db = self.client.splatoon_recruitment

    # initiate a record
    # return 0 if success
    def initiate(self, group = "", groups = "", public = True, owner = "", lock = False,
               kind = "", topic = "", time = "", goal = "",  requirement = "", open = True, player = ""):
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

        # create a record
        record = {"num" : num, "owner" :owner, "group":group, "groups":groups, "lock": lock,
                    "public": public, "topic":topic, "time":time, 
                    "goal":goal, "requirement":requirement, "open":open, "players":[player]}
        
        # insert the record
        self.db[kind].insert_one(record)
        return 0
    
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
        tmp = list(self.db[kind].find({"public":True, "open":True, "lock" : False}))
        # find all records that are open but not public
        tmp2 = list(self.db[kind].find({"public":False, "open":True, "lock" : False}))
        tmp2 = [i for i in tmp2 if group in i["groups"]]
        # combine the two lists
        re = tmp + tmp2
        return re
    
    # find a record by num
    # return a record
    def find_by_num(self, kind = "", num = ""):
        re = self.db[kind].find_one({"num":num})
        return re
    
    # find public and unlocked recruitment
    # return a list
    def find_public_unlocked(self, kind = "", group = ""):
        re = list(self.db[kind].find({"public":True, "lock":False, open:True}))
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
    # return 0 if success 1 otherwise
    def join(self, kind = "", group = "", num = "", player = ""):
        record = self.find_by_num(kind, num)
        if record.get("lock") == True or len(record.get("players")) >= 4:
            return 1
        # update the players of the record
        self.db[kind].update_one({"num":num}, {"$push":{"players":player}})
        return 0

    # leave a recruitment
    # return 0 if success 1 otherwise
    def leave(self, kind = "", group = "", num = "", player = ""):
        record = self.find_by_num(kind, num)
        if record.get("lock") == True:
            return 1
        # update the players of the record
        self.db[kind].update_one({"num":num}, {"$pull":{"players":player}})
        return 0

    # lock a recruitment
    def lock(self, kind = "", group = "", owner = "", num = ""):
        record = self.find_by_num(kind, num)
        # update the lock status of the record
        try:
            self.db[kind].update_one({"num":num, "owner":owner}, {"$set":{"lock":True}})
            return 0
        except:
            return 1

    # unlock a recruitment
    def unlock(self, kind = "", group = "", owner = "", num = ""):
        record = self.find_by_num(kind, num)
        # update the lock status of the record
        try:
            self.db[kind].update_one({"num":num, "owner":owner}, {"$set":{"lock":False}})
            return 0
        except:
            return 1
    