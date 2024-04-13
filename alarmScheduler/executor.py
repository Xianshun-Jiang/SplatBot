try:
    from  alarmScheduler.redisRouter import *
    from alarmScheduler.scheduler import *
except:
    import redisRouter
    import scheduler
from datetime import datetime
from robot import Robot



s = scheduler()

# r = redisRouter()
def execute(robot: Robot):
    time = datetime.now().strftime("%H:%M")
    insts = s.get_instruction(time)
    print(time)
    if insts != []:
        for inst in insts:
            self = robot
            group = inst.split('"')[3]
            wxid = inst.split('"')[5]
            wxid_new = f" @{self.wcf.get_alias_in_chatroom(wxid, group)}"
            msg = inst.split('"')[1]
            inst = inst.replace(msg, f"{wxid_new}\\n{msg}")
            # print(inst)
            exec(inst)
        self.alarmScheduler.reset_key(time)
