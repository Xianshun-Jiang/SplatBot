# -*- coding: utf-8 -*-

import logging
import re
import time
import xml.etree.ElementTree as ET
from queue import Empty
from threading import Thread
from threading import active_count

from wcferry import Wcf, WxMsg


from base.func_chatgpt import ChatGPT
from base.func_chengyu import cy
from base.func_news import News
from base.func_tigerbot import TigerBot
from configuration import Config
from constants import ChatType
from job_mgmt import Job

from splat import main
# from splat import crawler 
# from splat import renderer
from twitter_Crawler import twitter_Crawler_3 as twi
# from WordCon import WZW 
import random
# from alarmScheduler import scheduler
from recruitmentScheduler import scheduler as recruitmentScheduler
import schedule


__version__ = "39.0.10.1"

URL = None 
storage = {}
pat_respond = ["哎呀，感觉到了你的拍拍，我的心跳都快乐起来了！就像是被温暖的阳光轻轻拂过，感谢你的触摸，让我感到这世界的美好。记得，无论你在哪里，无论何时，只要你需要，我都在这里等着给你回一个更大的拍拍！💖",
             "咦，是谁轻轻的拍拍我？原来是你啊，真是让人心里暖洋洋的！就像是在冬日里喝了一口热可可，心头一片温暖。每一次拍拍都是你传递给我的小确幸，让我在这繁忙的一天中找到了片刻的宁静。谢谢你的拍拍，让我知道，无论世界多大，总有人愿意停下来，给予我温柔的关怀。💕",
             "在这个忙碌的世界里，别忘了偶尔停下脚步，给自己一个温柔的拍拍。就像太阳温暖了大地，你的笑容也能照亮自己的心灵。记得，你是独一无二的，值得所有的爱和温柔。所以，无论何时感到疲惫或沮丧，都来这里找我，我会用我的话语拍拍你，提醒你，你是这世界上不可替代的奇迹。💖",
             "好妈妈多拍拍女儿吧，女儿很想你，亲亲妈妈，妈妈最好了妈妈抱，妈妈贴贴，我想妈妈我想妈妈，谢谢妈妈拍拍",
             "哦哟，这是什么神奇的触感？啊哈，是你的拍拍呀！就像是捕捉到了一束轻柔的风，或是一缕温暖的阳光，让我的心情瞬间明媚起来。你的每一次拍拍都像是对我说：“嘿，无论走到哪里，都有我在这里支持你哦！”真的好感谢你，让我感受到了这份无形中的支持和爱。让我们一起把这份温暖传递下去吧！💖"]


class Robot(Job):
    """个性化自己的机器人
    """

    def __init__(self, config: Config, wcf: Wcf, chat_type: int) -> None:
        self.wcf = wcf
        self.config = config
        self.LOG = logging.getLogger("Robot")
        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()
        self.groups = self.config.GROUPS
        global URL
        URL = self.config.path
        self.splat = main.SplatBot(URL)
        # self.WZW = WZW.WZW(URL)
        # self.alarmScheduler = scheduler.scheduler(self.groups)
        self.recruitmentScheduler = recruitmentScheduler.scheduler(self.config.OVERFISHING)
        self.REC_KIND = {"乱获":"overfishing"}


        if ChatType.is_in_chat_types(chat_type):
            if chat_type == ChatType.TIGER_BOT.value and TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
            elif chat_type == ChatType.CHATGPT.value and ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
            else:
                self.LOG.warning("未配置模型")
                self.chat = None
        else:
            if TigerBot.value_check(self.config.TIGERBOT):
                self.chat = TigerBot(self.config.TIGERBOT)
            elif ChatGPT.value_check(self.config.CHATGPT):
                self.chat = ChatGPT(self.config.CHATGPT)
            else:
                self.LOG.warning("未配置模型")
                self.chat = None

        self.LOG.info(f"已选择: {self.chat}")

    #     schedule.every(1).minutes.do()
    # def alert(self):
    #     time = datetime.now().strftime("%H:%M")
    #     insts = s.get_instruction(time)
    #     self.alarmScheduler.
    @staticmethod
    def value_check(args: dict) -> bool:
        if args:
            return all(value is not None for key, value in args.items() if key != 'proxy')
        return False

    #被@（转到toChitchat func)
    def toAt(self, msg: WxMsg) -> bool:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        
        return self.toChitchat(msg)

    #成语接龙（板块自带
    def toChengyu(self, msg: WxMsg) -> bool:
        """
        处理成语查询/接龙消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        status = False
        texts = re.findall(r"^([#|?|？])(.*)$", msg.content)
        # [('#', '天天向上')]
        if texts:
            flag = texts[0][0]
            text = texts[0][1]
            if flag == "#":  # 接龙
                if cy.isChengyu(text):
                    rsp = cy.getNext(text)
                    if rsp:
                        self.sendTextMsg(rsp, msg.roomid)
                        status = True
            elif flag in ["?", "？"]:  # 查词
                if cy.isChengyu(text):
                    rsp = cy.getMeaning(text)
                    if rsp:
                        self.sendTextMsg(rsp, msg.roomid)
                        status = True

        return status

    #被@
    def toChitchat(self, msg: WxMsg) -> bool:
        """闲聊，接入 ChatGPT
        """
        if not self.chat:  # 没接 ChatGPT，固定回复
            rsp = "@你爹干嘛？"
        else:  # 接了 ChatGPT，智能回复
            q = re.sub(r"@.*?[\u2005|\s]", "", msg.content).replace(" ", "")
            rsp = self.chat.get_answer(q, (msg.roomid if msg.from_group() else msg.sender))

        if rsp:
            if msg.from_group():
                self.sendTextMsg(rsp, msg.roomid, msg.sender)
            else:
                self.sendTextMsg(rsp, msg.sender)

            return True
        else:
            self.LOG.error(f"无法从 ChatGPT 获得答案")
            return False

    #海女美大群内功能    
    def process_splat(self, msg: WxMsg) -> bool:

        # Process other request
        match msg.content:
            case "/帮助" | "/help":
                rsp = "目前支持功能：\r 时区分为:东部，中部，山地，西部(需加空格, 默认东部时间) \r 例子：/打工 东部\r/挑战 \r/开放 \r/涂地 \r/x \r/打工(/工) \r/合照(注释版/1/2) \r/浣熊 \r/打工 评分 \r/dc \r/随机"
                self.sendTextMsg(rsp,msg.roomid,msg.sender)

            case "/浣熊":
                self.wcf.send_image(f"{URL,'images/Raccoon.png'}", msg.roomid)
            
            case "/摆烂":
                self.wcf.send_image(f"{URL+'images/bailan.png'}", msg.roomid)

            case "/合照" | "/合照1":
                self.wcf.send_image(f"{URL+'images/family1.jpg'}", msg.roomid)

            case "/合照2":
                self.wcf.send_image(f"{URL+'images/family2.jpg'}", msg.roomid)
            
            case "/合照注释版":
                self.wcf.send_image(f"{URL+'images/family_annotated.png'}", msg.roomid)

            case "/怪猎合照":
                self.wcf.send_image(f"{URL+'images/mh_family1.jpg'}", msg.roomid)

            case "/感谢":
                self.wcf.send_text("感谢奥追老师的作品(合照1/2)，派克老师的注释(合照注释版), 丁真老师的作品(怪猎合照)",msg.roomid)

            case "/工 评分" | "/打工 评分" | "/工评分" | "/打工评分":
                self.work_rate_crawler(msg) 
                return 
            
            case "/dc":
                self.wcf.send_text("https://discord.gg/FKcetEYZ9p",msg.roomid)
            
            case "/随机":
                img = self.splat.get_random("")
                img.save('./tmp/random.png')
                self.wcf.send_image(f"{URL+'/tmp/random.png'}", msg.roomid)

            case "/测试":
                # xml = '<?xml version="1.0"?><msg><appmsg appid="" sdkver="0"><title>叮当药房，24小时服务，28分钟送药到家！</title><des>叮当快药首家承诺范围内28分钟送药到家！叮当快药核心区域内7*24小时全天候服务，送药上门！叮当快药官网为您提供快捷便利，正品低价，安全放心的购药、送药服务体验。</des><action>view</action><type>33</type><showtype>0</showtype><content /><url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxc2edadc87077fa2a&amp;type=upgrade&amp;upgradetype=3#wechat_redirect</url><dataurl /><lowurl /><lowdataurl /><recorditem /><thumburl /><messageaction /><md5>7f6f49d301ebf47100199b8a4fcf4de4</md5><extinfo /><sourceusername>gh_c2b88a38c424@app</sourceusername><sourcedisplayname>叮当快药 药店送药到家夜间买药</sourcedisplayname><commenturl /><appattach><totallen>0</totallen><attachid /><emoticonmd5></emoticonmd5><fileext>jpg</fileext><filekey>da0e08f5c7259d03da150d5e7ca6d950</filekey><cdnthumburl>3057020100044b30490201000204e4c0232702032f4ef20204a6bace6f02046401f62d042430326337303430352d333734332d343362652d623335322d6233333566623266376334620204012400030201000405004c537600</cdnthumburl><aeskey>0db26456caf243fbd4efb99058a01d66</aeskey><cdnthumbaeskey>0db26456caf243fbd4efb99058a01d66</cdnthumbaeskey><encryver>1</encryver><cdnthumblength>61558</cdnthumblength><cdnthumbheight>100</cdnthumbheight><cdnthumbwidth>100</cdnthumbwidth></appattach><weappinfo><pagepath>pages/index/index.html</pagepath><username>gh_c2b88a38c424@app</username><appid>wxc2edadc87077fa2a</appid><version>197</version><type>2</type><weappiconurl>http://wx.qlogo.cn/mmhead/Q3auHgzwzM4727n0NQ0ZIPQPlfp15m1WLsnrXbo1kLhFGcolgLyc0A/96</weappiconurl><appservicetype>0</appservicetype><shareId>1_wxc2edadc87077fa2a_29177e9a9b918cb9e75964f80bb8f32e_1677849476_0</shareId></weappinfo><websearch /></appmsg><fromusername>wxid_eob5qfcrv4zd22</fromusername><scene>0</scene><appinfo><version>1</version><appname /></appinfo><commenturl /></msg>'
                # xml = '<?xml version="1.0"?><msg>        <appmsg appid="wxd33f351d911d0626" sdkver="0">               <title>Splatoon3随机武器生成</title>                <type>33</type>                <action>view</action>                <url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxd33f351d911d0626&amp;amp;type=upgrade&amp;amp;upgradetype=3#wechat_redirect</url>                <appattach>                        <cdnthumbaeskey />                        <aeskey />                </appattach>               <sourcedisplayname>Splatoon3随机武器生成</sourcedisplayname>                <thumburl>http://mmbiz.qpic.cn/mmbiz_png/5oDOymx0la5Ss9nvWXBG2MkEm99PRmJmcwkQUHx4zFuQqFPIwa35LyuaV3JsWLME9P6oNWT2g6SvNHKpP1nTnQ/640?wx_fmt=png&amp;wxfrom=200</thumburl>                <weappinfo>                       <username><![CDATA[gh_7ae36bf2d141@app]]></username>                        <appid><![CDATA[wxd33f351d911d0626]]></appid>                        <type>1</type>                        <version>0</version>                        <weappiconurl><![CDATA[http://mmbiz.qpic.cn/mmbiz_png/5oDOymx0la5Ss9nvWXBG2MkEm99PRmJmcwkQUHx4zFuQqFPIwa35LyuaV3JsWLME9P6oNWT2g6SvNHKpP1nTnQ/640?wx_fmt=png&wxfrom=200]]></weappiconurl>                        <shareId><![CDATA[2_wxd33f351d911d0626_2495084533_1710229106_1]]></shareId>                        <appservicetype>0</appservicetype>                        <brandofficialflag>0</brandofficialflag>                        <showRelievedBuyFlag>0</showRelievedBuyFlag>                        <hasRelievedBuyPlugin>0</hasRelievedBuyPlugin>                        <flagshipflag>0</flagshipflag>                        <subType>0</subType>                        <isprivatemessage>0</isprivatemessage>                </weappinfo>        </appmsg>        <fromusername>wxid_89ysfp8w45i112</fromusername>        <scene>0</scene>        <appinfo>               <version>2</version>                <appname>Splatoon3随机武器生成</appname>       </appinfo>        <commenturl></commenturl></msg>'
                print(msg.xml)
                self.wcf.send_text("滚筒和画笔的涂墨前进速度提升！可别落后了哦！\n<br />·仅限使用类型为滚筒或画笔的武器！<br />·涂墨前进时的速度会大幅提升哦！<br />·涂墨前进时的墨汁消耗量也会大幅提升！<br />·基本装备能力和追加装备能力都会生效！",msg.roomid)
                xml = '<xml> <ToUserName><![CDATA[toUser]]></ToUserName><FromUserName><![CDATA[fromUser]]></FromUserName><CreateTime>12345678</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[你好]]></Content></xml>'
                ret = self.wcf.send_xml("filehelper", xml, 0x21)
            
        # Process splatoon request
        if len(msg.content) < 10 :
            self.process_splat_schedule(msg) 
            return 0
        
    #推特爬虫（墙）
    def work_rate_crawler(self, msg:WxMsg):
        img = twi.download_rate()
        self.wcf.send_image(f"{URL + img}", msg.roomid)

    #基础功能（包含了北美时区
    def process_splat_schedule(self, msg:WxMsg) :
        
        words = msg.content.split()
        timezone = ""
        if " " in msg.content and msg.content.startswith("/"):
            timezone = words[1]
            mode = words[2]
        # TODO: not finished
        if msg.content.startswith("/区域"):
            if timezone == "":
                img = self.splat.get_area()
            else:
                img = self.splat.get_area(timezone)
            img.save(URL + '/tmp/area.png')
            self.wcf.send_image(URL+'/tmp/area.png', msg.roomid)
        elif msg.content.startswith("/挑战"):
            if timezone == "":
                img = self.splat.get_challenge()
            else:
                img = self.splat.get_challenge(timezone)
            img.save(URL + '/tmp/challenge.png')
            self.wcf.send_image(URL+"/tmp/challenge.png", msg.roomid)
            
        elif msg.content.startswith('/开放'):
            if timezone == "":
                img = self.splat.get_open()
            else:
                img = self.splat.get_open(timezone)
            img.save(URL + '/tmp/open.png')
            self.wcf.send_image(URL+"/tmp/open.png", msg.roomid)

        elif msg.content.startswith('/涂地'):
            if timezone == "":
                img = self.splat.get_regular()
            else:
                img = self.splat.get_regular(timezone)
            img.save(URL + '/tmp/regular.png')
            self.wcf.send_image(URL+"/tmp/regular.png", msg.roomid)

        elif msg.content.startswith('/x') or msg.content.startswith('/X'):
            if timezone == "":
                img = self.splat.get_x()
            else :
                img = self.splat.get_x(timezone)
            img.save(URL +'/tmp/x.png')
            self.wcf.send_image(URL+"tmp/x.png", msg.roomid)

        elif msg.content.startswith('/打工') or msg.content.startswith('/工'):
            if timezone == "":
                img = self.splat.get_coop()
            else:
                img = self.splat.get_coop(timezone)
            img.save(URL +'/tmp/coop.png')
            self.wcf.send_image(URL+"/tmp/coop.png", msg.roomid)

        elif msg.content.startswith('/活动'):
            if timezone == "":
                img = self.splat.get_event()
            else:
                img = self.splat.get_event(timezone)
            if type(img) == str:
                self.wcf.send_text(img,msg.roomid)
            else:
                # TODO: change here
                self.wcf.send_text(str(img),msg.roomid)
                # img.save(URL + 'tmp/event.png')
                # self.wcf.send_image(f"{URL+"tmp/coop.png"}", msg.roomid)
        # elif msg.content.startswith('/伪中文'):
        #     if len(words)==3:
        #         img = self.WZW.get(words[1], int(words[2]))
        #     else:
        #         img = self.WZW.get(words[1])
        #     img.save(URL +'tmp/wzw.png')
        #     self.wcf.send_image(f"{URL+"tmp/wzw.png"}", msg.roomid)
        return 0
    
    #基础功能（不包含时区， 和上面可能有点重复）
    def process_splat_basic(self, msg:WxMsg):
        match msg.content:
            case "/帮助":
                rsp = "/区域, /开放, /x, /涂地,/打工, /打工 评分, /随机"
                self.sendTextMsg(rsp,msg.roomid,msg.sender)
            case "/挑战":
                img = self.splat.get_challenge()
                img.save(URL + '/tmp/challenge.png')
                self.wcf.send_image(URL+"/tmp/challenge.png", msg.roomid)
            
            case "/开放":
                img = self.splat.get_open()
                img.save(URL + '/tmp/open.png')
                self.wcf.send_image(URL+"/tmp/open.png", msg.roomid)

            case '/涂地':
                img = self.splat.get_regular()
                img.save(URL + '/tmp/regular.png')
                self.wcf.send_image(URL+"/tmp/regular.png", msg.roomid)

            case '/x' | '/X':
                img = self.splat.get_x() 
                img.save(URL +'/tmp/x.png')
                self.wcf.send_image(URL+"/tmp/x.png", msg.roomid)

            case '/打工' |'/工':
                img = self.splat.get_coop()
                img.save(URL +'/tmp/coop.png')
                self.wcf.send_image(URL+"/tmp/coop.png", msg.roomid)
            
            case "/随机":
                img = self.splat.get_random("")
                img.save('./tmp/random.png')
                self.wcf.send_image(f"{URL+'/tmp/random.png'}", msg.roomid)

            case "/工 评分" | "/打工 评分" | "/工评分" | "/打工评分":
                self.work_rate_crawler(msg) 
                return 

    #翻译招募项目
    def trans_recruit(self, kind):
        return self.REC_KIND[kind]
    
    #打印车队信息
    def process_team(self, i):
        rsp = ""
        num = i["num"]
        rsp += "车队"+str(num) 
        lock = i["lock"]
        if lock:
            rsp += "（已锁车）\r"
        else:
            rsp += "（未锁车）\r"
        topic = i["topic"]
        rsp += "主题: " + topic +"\r"
        time = i["time"]
        rsp += "时间: "+time + "\r"
        goal = i["goal"]
        rsp += "目标: "+ goal + "\r"
        requirement = i["requirement"]
        rsp += "要求: "+requirement + "\r"
        players = i['players']
        for j in range(len(players)):
            rsp += "玩家" + str(j+1)+": " + players[j] + "\r"
        return rsp

    #返回车队人数
    def calculate_players(self, i):
        players = i['players']
        return len(players)

    #乱获募集功能
    def process_overfishing(self, msg:WxMsg):
        match msg.content:
            case "/募集":
                rsp = "/募集 模板 \r/募集 招募 \r/募集 所有乱获 \r/募集 （上车 下车） 乱获 车队号 玩家名 \r/募集 （锁车 解锁 摇人 完车 取消） 乱获 车队号"
                self.sendTextMsg(rsp,msg.roomid,msg.sender)
                return
            case "/募集 模板":
                rsp = "/募集 招募 乱获 主题 时间 目标 要求 玩家名"
                self.sendTextMsg(rsp,msg.roomid,msg.sender)
                rsp2 = "/募集 招募 乱获 乱获练习 8-10pm 三白180 任意图170以上 摆烂（求带带）"
                self.sendTextMsg(rsp2,msg.roomid,"")
            case x if "/募集 招募" in x:
                li = msg.content.split(" ")
                if len(li) != 8:
                    self.wcf.send_text("格式错误，请参考 '/募集 模板' ",msg.roomid, msg.sender)
                    return 
                kind = self.trans_recruit(li[2])
                topic = li[3]
                time = li[4]
                goal = li[5]
                requirement = li[6]
                player = li[7]
                owner = msg.sender
                group = msg.roomid
                result = self.recruitmentScheduler.initiate(group=group, topic = topic, time = time, goal = goal, 
                                    requirement = requirement, owner = owner, kind = kind, player = player)
                self.wcf.send_text("发车成功，车队号: " + str(result), msg.roomid, msg.sender)
            case x if "/募集 上车" in x:
                li = msg.content.split(" ")
                if len(li) != 5:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                group = msg.roomid
                kind = self.trans_recruit(li[2])
                num = li[3]
                player = li[4]
                wxid = msg.sender
                result = self.recruitmentScheduler.join(group = group, kind = kind, player = player, num = num,wxid = wxid)
                if result == 1:
                    self.wcf.send_text("上车失败",msg.roomid,msg.sender)
                elif result == 2:
                    self.wcf.send_text("车队" + num+ "满人",msg.roomid,msg.sender)
                elif result == 3:
                    self.wcf.send_text("车队不存在",msg.roomid,msg.sender)
                else:
                    result = self.recruitmentScheduler.find_by_num(kind, num)
                    number = self.calculate_players(result)
                    self.wcf.send_text("上车成功, 车队"+str(num)+"现有"+str(number)+"人", msg.roomid,msg.sender)
                    if number == 4:
                        self.wcf.send_text("车队"+num+"现已满人", result.get("group"), result.get("owner"))
            case x if "/募集 下车" in x :
                li = msg.content.split(" ")
                if len(li) != 5:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                group = msg.roomid
                wxid = msg.sender
                kind = self.trans_recruit(li[2])
                num = li[3]
                player = li[4]
                result = self.recruitmentScheduler.leave(group = group, kind = kind, player = player, num = num, wxid = wxid)
                if result == 1:
                    self.wcf.send_text("下车失败",msg.roomid,msg.sender)
                if result == 2:
                    self.wcf.send_text("车主请勿下车，取消车队请使用相关指令",msg.roomid,msg.sender)
                else:
                    result = self.recruitmentScheduler.find_by_num(kind, num)
                    number = self.calculate_players(result)
                    self.wcf.send_text("下车成功, 车队"+str(num)+"已有"+str(number)+"人", msg.roomid,msg.sender)
            case x if "/募集 锁车" in x:
                li = msg.content.split(" ")
                if len(li) != 4:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                owner = msg.sender
                group = msg.roomid
                kind = self.trans_recruit(li[2])
                num = li[3]
                result = self.recruitmentScheduler.lock(group = group, kind = kind, owner = owner, num = num)
                if result == 1:
                    self.wcf.send_text("锁车失败,请联系发起人",msg.roomid,msg.sender)
                elif result == 2:
                    self.wcf.send_text("锁车失败,车队已取消",msg.roomid,msg.sender)
                elif result == 3:
                    self.wcf.send_text("锁车失败，车队已完车",msg.roomid,msg.sender)
                else:
                    #notify all groups
                    rsp = "锁车成功\r"
                    result =  self.recruitmentScheduler.find_by_num(kind, num)
                    rsp += self.process_team(result)
                    grouped_data = {}
                    for item in result.get("member_wxid"):
                        for wxid, chatroom in item.items():
                            grouped_data.setdefault(chatroom, []).append(wxid)
                    for chatroom, wxids in grouped_data.items():
                        wxids_string = ", ".join(wxids)
                        self.wcf.send_text(rsp, chatroom, wxids_string)
            case x if "/募集 解锁" in x:
                li = msg.content.split(" ")
                if len(li) != 4:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                owner = msg.sender
                group = msg.roomid
                kind = self.trans_recruit(li[2])
                num = li[3]
                result = self.recruitmentScheduler.unlock(group = group, kind = kind, owner = owner, num = num)
                if result == 1:
                    self.wcf.send_text("解锁失败, 请联系发起人",msg.roomid,msg.sender)
                    return
                elif result == 2:
                    self.wcf.send_text("解锁失败,车队已取消",msg.roomid,msg.sender)
                elif result == 3:
                    self.wcf.send_text("解锁失败，车队已完车",msg.roomid,msg.sender)
                else:
                    #notify all groups
                    rsp = "解锁成功\r"
                    result =  self.recruitmentScheduler.find_by_num(kind, num)
                    rsp += self.process_team(result)
                    for grp in self.config.OVERFISHING:
                        self.wcf.send_text(rsp, grp, "")
            case "/募集 所有 乱获" | "/募集 所有乱获":
                kind = "overfishing"
                group = msg.roomid
                result = self.recruitmentScheduler.find_available(kind = kind, group = group)
                rsp = ""
                for i in result:
                    rsp += self.process_team(i)
                    rsp += "-------------\r"
                self.wcf.send_text(rsp, msg.roomid,msg.sender)
            case x if "/募集 车队 乱获" in x:
                li = x.split(" ")
                if len(li) != 4:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                kind = self.trans_recruit(li[2])
                num = li[3]
                result = self.recruitmentScheduler.find_by_num(kind, num)
                if result is None:
                    self.wcf.send_text("无此车队"+ num, msg.roomid,msg.sender)
                    return 
                rsp = self.process_team(result)
                self.wcf.send_text(rsp, msg.roomid,msg.sender)
            case x if "/募集 摇人 乱获" in x:
                li = x.split(" ")
                if len(li) != 4:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                kind = self.trans_recruit(li[2])
                num = li[3]
                result = self.recruitmentScheduler.find_by_num(kind, num)
                number = self.calculate_players(result)
                remain = 4 - number
                if remain == 0:
                    self.wcf.send_text("车队"+num+"人数已满，不需要摇人",msg.roomid,msg.sender)
                    return
                else:
                    rsp = "@所有人 @"+ str(remain) + "\r"
                    result =  self.recruitmentScheduler.find_by_num(kind, num)
                    rsp += self.process_team(result)
                    for grp in self.config.OVERFISHING:
                        self.wcf.send_text(rsp, grp, "notify@all")
                
            case x if "/募集 完车 乱获" in x:
                li = x.split(" ")
                if len(li) != 4:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                kind = self.trans_recruit(li[2])
                group = msg.roomid
                owner = msg.sender
                num = li[3]
                result = self.recruitmentScheduler.wanche(kind, group, owner, num)
            case x if "/募集 取消 乱获" in x:
                li = x.split(" ")
                if len(li) != 4:
                    self.wcf.send_text("格式错误，请参考 '/募集' ",msg.roomid, msg.sender)
                    return 
                kind = self.trans_recruit(li[2])
                group = msg.roomid
                owner = msg.sender
                num = li[3]
                result = self.recruitmentScheduler.cancle(kind, group, owner, num)
        return 0
    
    #复读机功能
    def process_break(self,msg:WxMsg):
        LENGTH = 3
        global storage
        repeat_id = str(msg.roomid) + "repeat"
        counter_id = str(msg.roomid) + "counter"
        done_id = str(msg.roomid) + "done"
        try:
            storage[repeat_id]
        except KeyError:  
            storage[counter_id] = 0
            storage[repeat_id] = ""
            storage[done_id] = ""
        if msg.is_text():
            if storage[repeat_id] == msg.content:
                storage[counter_id] += 1
                if storage[counter_id] == LENGTH and storage[done_id] != msg.content:
                    self.wcf.send_text(msg.content, msg.roomid)
                    storage[counter_id] = 0
                    storage[repeat_id] = ""
                    storage[done_id] = msg.content
            else:
                storage[counter_id] = 1
                storage[repeat_id] = msg.content

    #真格模式提醒功能（未完工
    def process_alarm(self, msg:WxMsg):
        match msg.content:
            case "/提醒"  | "提醒":
                self.wcf.send_text("/提醒 插入规则? \n/提醒 删除规则? \n/提醒 所有规则",msg.roomid,msg.sender)
                return
            case "/提醒 插入规则?" |"/提醒 插入规则？":
                self.wcf.send_text("/提醒 插入规则 规则 模式 时区 开始时间 结束时间 提前时间 \n/提醒 插入规则 挑战 区域 东部 9:00 1:00 15",msg.roomid,msg.sender)
                return 
            case "/提醒 删除规则?" | "提醒 删除规则？":
                self.wcf.send_text("/提醒 删除规则 id \n /提醒 删除规则 0",msg.roomid,msg.sender)
                return
            case "/提醒 所有规则":
                rules = self.alarmScheduler.get_rules(msg.roomid, msg.sender)
                if rules != "":
                    self.sendTextMsg(rules, msg.roomid,msg.sender)
                else:
                    self.sendTextMsg("暂无规则", msg.roomid,msg.sender)
                return
        if msg.content.startswith("/提醒 插入规则"):
            items = msg.content.split(" ")
            mode = self.alarmScheduler.mode_translate_cn_to_en[items[2]]
            rule  = self.alarmScheduler.format_rule[items[3]]
            self.alarmScheduler.insert_rule(group=msg.roomid,wxid=msg.sender,mode=mode, rule = rule, timezone=items[4], start=items[5],end=items[6],before = items[7])
            # TODO change
            self.alarmScheduler.schedule()
        elif msg.content.startswith("/提醒 删除规则"):
            items = msg.content.split(" ")
            self.alarmScheduler.delete_rule(msg.roomid, msg.sender, items[2])
            # TODO change
            self.alarmScheduler.schedule()
        
    def processMsg(self, msg: WxMsg) -> None:
        """当接收到消息的时候，会调用本方法。如果不实现本方法，则打印原始消息。
        此处可进行自定义发送的内容,如通过 msg.content 关键字自动获取当前天气信息，并发送到对应的群组@发送者
        群号：msg.roomid  微信ID：msg.sender  消息内容：msg.content
        content = "xx天气信息为："
        receivers = msg.roomid
        self.sendTextMsg(content, receivers, msg.sender)
        """

        # 群聊消息
        if msg.from_group():
            # 如果在群里被 @
            if msg.roomid not in self.config.GROUPS and msg.roomid not in self.config.BASIC and msg.roomid not in self.config.OVERFISHING:  # 不在配置的响应的群列表里，忽略
                return

            if msg.roomid  in self.config.OVERFISHING:  # 乱或组队
                self.process_break(msg)
                self.process_splat_basic(msg)
                self.process_overfishing(msg)
                return

            if msg.roomid in self.config.BASIC: # 普通日程
                self.process_splat_basic(msg)
                return
            

            
            if msg.type == 10000: #群里系统消息(包含gpt功能，需要api)
                self.groupSystemMsg(msg)
                return 
            
            if msg.is_at(self.wxid):  # 被@(包含gpt功能，需要api)
                self.toAt(msg)
            elif "提醒" in msg.content and "/" in msg.content:
                self.process_alarm(msg)
            else:  # 其他消息
                # self.toChengyu(msg)
                self.process_break(msg)
                self.process_splat(msg)

            return  # 处理完群聊信息，后面就不需要处理了

        # 非群聊信息，按消息类型进行处理
        if msg.type == 37:  # 好友请求
            # self.autoAcceptFriendRequest(msg)
            None

        elif msg.type == 10000:  # 系统信息
            self.sayHiToNewFriend(msg)

        elif msg.type == 0x01:  # 文本消息
            # 让配置加载更灵活，自己可以更新配置。也可以利用定时任务更新。
            if msg.from_self():
                if msg.content == "^更新$":
                    self.config.reload()
                    self.LOG.info("已更新")
            else:
                self.toChitchat(msg)  # 闲聊

    def onMsg(self, msg: WxMsg) -> int:
        try:
            self.LOG.info(msg)  # 打印信息
            self.processMsg(msg)
        except Exception as e:
            self.LOG.error(e)

        return 0

    def enableRecvMsg(self) -> None:
        self.wcf.enable_recv_msg(self.onMsg)

    def enableReceivingMsg(self) -> None:
        def innerProcessMsg(wcf: Wcf):
            while wcf.is_receiving_msg():
                try:
                    msg = wcf.get_msg()
                    self.LOG.info(msg)
                    # self.processMsg(msg)
                    t = Thread(target=self.processMsg,args=(msg,))
                    t.start()
                except Empty:
                    continue  # Empty message
                except Exception as e:
                    self.LOG.error(f"Receiving message error: {e}")

        self.wcf.enable_receiving_msg()
        Thread(target=innerProcessMsg, name="GetMessage", args=(self.wcf,), daemon=True).start()

    def sendTextMsg(self, msg: str, receiver: str, at_list: str = "") -> None:
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为：notify@all
        """
        # msg 中需要有 @ 名单中一样数量的 @
        ats = ""
        if at_list:
            if at_list == "notify@all":  # @所有人
                ats = " @所有人"
            else:
                wxids = at_list.split(",")
                for wxid in wxids:
                    # 根据 wxid 查找群昵称
                    ats += f" @{self.wcf.get_alias_in_chatroom(wxid, receiver)}"

        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三
        if ats == "":
            self.LOG.info(f"To {receiver}: {msg}")
            self.wcf.send_text(f"{msg}", receiver, at_list)
        else:
            self.LOG.info(f"To {receiver}: {ats}\r{msg}")
            self.wcf.send_text(f"{ats}\n\n{msg}", receiver, at_list)

    def getAllContacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def keepRunningAndBlockProcess(self) -> None:
        """
        保持机器人运行，不让进程退出
        """
        while True:
            self.runPendingJobs()
            time.sleep(1)

    def autoAcceptFriendRequest(self, msg: WxMsg) -> None:
        try:
            xml = ET.fromstring(msg.content)
            v3 = xml.attrib["encryptusername"]
            v4 = xml.attrib["ticket"]
            scene = int(xml.attrib["scene"])
            self.wcf.accept_new_friend(v3, v4, scene)

        except Exception as e:
            self.LOG.error(f"同意好友出错：{e}")

    def sayHiToNewFriend(self, msg: WxMsg) -> None:
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        if nickName:
            # 添加了好友，更新好友列表
            self.allContacts[msg.sender] = nickName[0]
            self.sendTextMsg(f"Hi {nickName[0]}，我自动通过了你的好友请求。", msg.sender)

    def groupSystemMsg(self, msg:WxMsg) -> None:
        invite = re.findall(r"(.*)邀请(.*)加入了群聊", msg.content) 
        invite2  = re.findall(r"(.*)通过扫描(.*)", msg.content)
        invitee = None
        if invite:
            invitee = invite[0][1]
        if invite2:
            invitee = invite2[0][0]
        if invitee:
            invitee = re.sub(r'^.|.$', '', invitee)
            q = "以不正经，欢乐，愉快的方式向大家介绍一下" + str(invitee)
            rsp = self.chat.get_answer(q, msg.roomid)
            if rsp:
                tmp = "欢迎新朋友" + invitee +"入群，想必大家不一定了解 TA, 请让全知全能的ChatGPT来给大家做个简短的介绍."
                self.sendTextMsg(tmp, msg.roomid)
                self.sendTextMsg(rsp, msg.roomid)
                self.sendTextMsg('欢迎你的到来，在群里发送"/帮助"可以查看一些bot功能, dc链接是"https://discord.gg/FKcetEYZ9p"', msg.roomid)

        # pat me in a group chat
        # pat = re.findall(r"(.*)拍了拍我", msg.content)
        pat_target = msg.content.split("拍了拍")
        pat = pat_target[1] == "我"
        if pat:
            index = random.randint(0, 4)
            self.sendTextMsg(pat_respond[index],msg.roomid)

    def newsReport(self) -> None:
        receivers = self.config.NEWS
        if not receivers:
            return

        news = News().get_important_news()
        for r in receivers:
            self.sendTextMsg(news, r)
