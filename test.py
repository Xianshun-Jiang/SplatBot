try:
    from  alarmScheduler.redisRouter import *
    from alarmScheduler.scheduler import *
except:
    import redisRouter
    import scheduler
from datetime import datetime
from robot import Robot

r = redisRouter()

r.insert
keys = r.get_all_keys()
for key in keys:
    print(key)
print(r.get_all_keys)

# inst = r.get("19:59")[0]
# wxid_new = "@kanade"
# msg = inst.split('"')[1]
# inst = inst.replace(msg, f"{wxid_new}\\n{msg}")
# print(inst)
s =scheduler()
s.schedule()
keys = r.get_all_keys()
for key in keys:
    print(key)
print(r.get_all_keys)

