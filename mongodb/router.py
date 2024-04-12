import  pymongo 
client = pymongo.MongoClient("localhost", 27017)
db = client.splatoon_wechat


group = "20770852617@chatroom"

record = {"wxid" :"", "mode":"challenge"}
db[group].insert_one(record)

print(db[group])
