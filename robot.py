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

from splat import main as splat
from splat import crawler 
from splat import renderer
from twitter_Crawler import twitter_Crawler_3 as twi

__version__ = "39.0.10.1"

URL = None 


class Robot(Job):
    """个性化自己的机器人
    """

    def __init__(self, config: Config, wcf: Wcf, chat_type: int) -> None:
        self.wcf = wcf
        self.config = config
        self.LOG = logging.getLogger("Robot")
        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()
        global URL
        URL = self.config.path

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

    @staticmethod
    def value_check(args: dict) -> bool:
        if args:
            return all(value is not None for key, value in args.items() if key != 'proxy')
        return False

    def toAt(self, msg: WxMsg) -> bool:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        
        return self.toChitchat(msg)

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
        
    def process_splat(self, msg: WxMsg) -> bool:

        # Process other request
        match msg.content:
            case "/帮助" | "/help":
                rsp = "目前支持功能：\r 时区分为:东部，中部，山地，西部(需加空格, 默认东部时间) \r 例子：/打工 东部\r/挑战 \r/开放 \r/涂地 \r/x \r/打工(/工) \r/合照(注释版/1/2) \r/浣熊 \r/打工 评分 \r/dc \r/随机"
                self.sendTextMsg(rsp,msg.roomid,msg.sender)

            case "/浣熊":
                self.wcf.send_image(f"{URL+"images/Raccoon.png"}", msg.roomid)
            
            case "/摆烂":
                self.wcf.send_image(f"{URL+"images/bailan.png"}", msg.roomid)

            case "/合照" | "/合照1":
                self.wcf.send_image(f"{URL+"images/family1.jpg"}", msg.roomid)

            case "/合照2":
                self.wcf.send_image(f"{URL+"images/family2.jpg"}", msg.roomid)
            
            case "/合照注释版":
                self.wcf.send_image(f"{URL+"images/family_annotated.png"}", msg.roomid)

            case "/怪猎合照":
                self.wcf.send_image(f"{URL+"images/mh_family1.jpg"}", msg.roomid)

            case "/感谢":
                self.wcf.send_text("感谢奥追老师的作品(合照1/2)，派克老师的注释(合照注释版), 丁真老师的作品(怪猎合照)",msg.roomid)

            case "/工 评分" | "/打工 评分" | "/工评分" | "/打工评分":
                img = twi.download_rate()
                self.wcf.send_image(f"{img}", msg.roomid)
                return 
            
            case "/dc":
                self.wcf.send_text("https://discord.gg/FKcetEYZ9p",msg.roomid)
            case "/随机":
                self.wcf.send_text("#小程序://随机武器/lThYUIeMXAJHYEB",msg.roomid)
                # self.wcf.send_xml(receiver= msg.roomid, type = 0x21, xml=
                                #   '<?xml version="1.0"?><msg>        <appmsg appid="wxd33f351d911d0626" sdkver="0">               <title>Splatoon3随机武器生成</title>                <type>33</type>                <action>view</action>                <url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxd33f351d911d0626&amp;amp;type=upgrade&amp;amp;upgradetype=3#wechat_redirect</url>                <appattach>                        <cdnthumbaeskey />                        <aeskey />                </appattach>               <sourcedisplayname>Splatoon3随机武器生成</sourcedisplayname>                <thumburl>http://mmbiz.qpic.cn/mmbiz_png/5oDOymx0la5Ss9nvWXBG2MkEm99PRmJmcwkQUHx4zFuQqFPIwa35LyuaV3JsWLME9P6oNWT2g6SvNHKpP1nTnQ/640?wx_fmt=png&amp;wxfrom=200</thumburl>                <weappinfo>                       <username><![CDATA[gh_7ae36bf2d141@app]]></username>                        <appid><![CDATA[wxd33f351d911d0626]]></appid>                        <type>1</type>                        <version>0</version>                        <weappiconurl><![CDATA[http://mmbiz.qpic.cn/mmbiz_png/5oDOymx0la5Ss9nvWXBG2MkEm99PRmJmcwkQUHx4zFuQqFPIwa35LyuaV3JsWLME9P6oNWT2g6SvNHKpP1nTnQ/640?wx_fmt=png&wxfrom=200]]></weappiconurl>                        <shareId><![CDATA[2_wxd33f351d911d0626_2495084533_1710229106_1]]></shareId>                        <appservicetype>0</appservicetype>                        <brandofficialflag>0</brandofficialflag>                        <showRelievedBuyFlag>0</showRelievedBuyFlag>                        <hasRelievedBuyPlugin>0</hasRelievedBuyPlugin>                        <flagshipflag>0</flagshipflag>                        <subType>0</subType>                        <isprivatemessage>0</isprivatemessage>                </weappinfo>        </appmsg>        <fromusername>wxid_89ysfp8w45i112</fromusername>        <scene>0</scene>        <appinfo>               <version>2</version>                <appname>Splatoon3随机武器生成</appname>       </appinfo>        <commenturl></commenturl></msg>')
                                #   '<?xml version="1.0"?><msgsource><bizflag>0</bizflag><tmp_node><publisher-id></publisher-id></tmp_node><alnode><fr>2</fr></alnode><sec_msg_node><uuid>10f67f7b9d70062f857af9ccb81c7f57_</uuid><risk-file-flag /><risk-file-md5-list /></sec_msg_node><silence>0</silence><membercount>3</membercount><signature>V1_7SsFuC7T|v1_LCidHjJv</signature></msgsource>')
                                # '<?xml version="1.0"?>#小程序://随机武器/lThYUIeMXAJHYEB')
            case "/测试":
                # xml = '<?xml version="1.0"?><msg><appmsg appid="" sdkver="0"><title>叮当药房，24小时服务，28分钟送药到家！</title><des>叮当快药首家承诺范围内28分钟送药到家！叮当快药核心区域内7*24小时全天候服务，送药上门！叮当快药官网为您提供快捷便利，正品低价，安全放心的购药、送药服务体验。</des><action>view</action><type>33</type><showtype>0</showtype><content /><url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxc2edadc87077fa2a&amp;type=upgrade&amp;upgradetype=3#wechat_redirect</url><dataurl /><lowurl /><lowdataurl /><recorditem /><thumburl /><messageaction /><md5>7f6f49d301ebf47100199b8a4fcf4de4</md5><extinfo /><sourceusername>gh_c2b88a38c424@app</sourceusername><sourcedisplayname>叮当快药 药店送药到家夜间买药</sourcedisplayname><commenturl /><appattach><totallen>0</totallen><attachid /><emoticonmd5></emoticonmd5><fileext>jpg</fileext><filekey>da0e08f5c7259d03da150d5e7ca6d950</filekey><cdnthumburl>3057020100044b30490201000204e4c0232702032f4ef20204a6bace6f02046401f62d042430326337303430352d333734332d343362652d623335322d6233333566623266376334620204012400030201000405004c537600</cdnthumburl><aeskey>0db26456caf243fbd4efb99058a01d66</aeskey><cdnthumbaeskey>0db26456caf243fbd4efb99058a01d66</cdnthumbaeskey><encryver>1</encryver><cdnthumblength>61558</cdnthumblength><cdnthumbheight>100</cdnthumbheight><cdnthumbwidth>100</cdnthumbwidth></appattach><weappinfo><pagepath>pages/index/index.html</pagepath><username>gh_c2b88a38c424@app</username><appid>wxc2edadc87077fa2a</appid><version>197</version><type>2</type><weappiconurl>http://wx.qlogo.cn/mmhead/Q3auHgzwzM4727n0NQ0ZIPQPlfp15m1WLsnrXbo1kLhFGcolgLyc0A/96</weappiconurl><appservicetype>0</appservicetype><shareId>1_wxc2edadc87077fa2a_29177e9a9b918cb9e75964f80bb8f32e_1677849476_0</shareId></weappinfo><websearch /></appmsg><fromusername>wxid_eob5qfcrv4zd22</fromusername><scene>0</scene><appinfo><version>1</version><appname /></appinfo><commenturl /></msg>'
                # xml = '<?xml version="1.0"?><msg>        <appmsg appid="wxd33f351d911d0626" sdkver="0">               <title>Splatoon3随机武器生成</title>                <type>33</type>                <action>view</action>                <url>https://mp.weixin.qq.com/mp/waerrpage?appid=wxd33f351d911d0626&amp;amp;type=upgrade&amp;amp;upgradetype=3#wechat_redirect</url>                <appattach>                        <cdnthumbaeskey />                        <aeskey />                </appattach>               <sourcedisplayname>Splatoon3随机武器生成</sourcedisplayname>                <thumburl>http://mmbiz.qpic.cn/mmbiz_png/5oDOymx0la5Ss9nvWXBG2MkEm99PRmJmcwkQUHx4zFuQqFPIwa35LyuaV3JsWLME9P6oNWT2g6SvNHKpP1nTnQ/640?wx_fmt=png&amp;wxfrom=200</thumburl>                <weappinfo>                       <username><![CDATA[gh_7ae36bf2d141@app]]></username>                        <appid><![CDATA[wxd33f351d911d0626]]></appid>                        <type>1</type>                        <version>0</version>                        <weappiconurl><![CDATA[http://mmbiz.qpic.cn/mmbiz_png/5oDOymx0la5Ss9nvWXBG2MkEm99PRmJmcwkQUHx4zFuQqFPIwa35LyuaV3JsWLME9P6oNWT2g6SvNHKpP1nTnQ/640?wx_fmt=png&wxfrom=200]]></weappiconurl>                        <shareId><![CDATA[2_wxd33f351d911d0626_2495084533_1710229106_1]]></shareId>                        <appservicetype>0</appservicetype>                        <brandofficialflag>0</brandofficialflag>                        <showRelievedBuyFlag>0</showRelievedBuyFlag>                        <hasRelievedBuyPlugin>0</hasRelievedBuyPlugin>                        <flagshipflag>0</flagshipflag>                        <subType>0</subType>                        <isprivatemessage>0</isprivatemessage>                </weappinfo>        </appmsg>        <fromusername>wxid_89ysfp8w45i112</fromusername>        <scene>0</scene>        <appinfo>               <version>2</version>                <appname>Splatoon3随机武器生成</appname>       </appinfo>        <commenturl></commenturl></msg>'
                print(msg.xml)
                xml = '<xml> <ToUserName><![CDATA[toUser]]></ToUserName><FromUserName><![CDATA[fromUser]]></FromUserName><CreateTime>12345678</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[你好]]></Content></xml>'
                ret = self.wcf.send_xml("filehelper", xml, 0x21)
            
        # Process splatoon request
        if len(msg.content) < 10 :
            words = msg.content.split()
            timezone = ""
            if " " in msg.content:
                timezone = words[1]
            if msg.content.startswith("/挑战"):
                if timezone == "":
                    img = splat.get_challenge()
                else:
                    img = splat.get_challenge(timezone)
                img.save('./tmp/challenge.png')
                self.wcf.send_image(f"{URL+"tmp/challenge.png"}", msg.roomid)
                
            elif msg.content.startswith('/开放'):
                if timezone == "":
                    img = splat.get_open()
                else:
                    img = splat.get_open(timezone)
                img.save('./tmp/open.png')
                self.wcf.send_image(f"{URL+"tmp/open.png"}", msg.roomid)

            elif msg.content.startswith('/涂地'):
                if timezone == "":
                    img = splat.get_regular()
                else:
                    img = splat.get_regular(timezone)
                img.save('./tmp/regular.png')
                self.wcf.send_image(f"{URL+"tmp/regular.png"}", msg.roomid)

            elif msg.content.startswith('/x') or msg.content.startswith('/X'):
                if timezone == "":
                    img = splat.get_x()
                else :
                    img = splat.get_x(timezone)
                img.save('./tmp/x.png')
                self.wcf.send_image(f"{URL+"tmp/x.png"}", msg.roomid)

            elif msg.content.startswith('/打工') or msg.content.startswith('/工'):
                if timezone == "":
                    img = splat.get_coop()
                else:
                    img = splat.get_coop(timezone)
                img.save('./tmp/coop.png')
                self.wcf.send_image(f"{URL+"tmp/coop.png"}", msg.roomid)
                
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
            if msg.roomid not in self.config.GROUPS:  # 不在配置的响应的群列表里，忽略
                return
            
            if msg.type == 10000: #群里系统消息
                self.groupSystemMsg(msg)
                return 

            if msg.is_at(self.wxid) or "@SplatoonZealot" in msg.content:  # 被@
                self.toAt(msg)
            else:  # 其他消息
                # self.toChengyu(msg)
                # print(msg.xml)
                self.process_splat(msg)

            return  # 处理完群聊信息，后面就不需要处理了

        # 非群聊信息，按消息类型进行处理
        if msg.type == 37:  # 好友请求
            self.autoAcceptFriendRequest(msg)

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
            invitee = invite[0][0]
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
        pat = re.findall(r"(.*)拍了拍我", msg.content)
        if pat:
            self.sendTextMsg("好妈妈多拍拍女儿吧，女儿很想你，亲亲妈妈，妈妈最好了妈妈抱，妈妈贴贴，我想妈妈我想妈妈，谢谢妈妈拍拍",msg.roomid)



    def newsReport(self) -> None:
        receivers = self.config.NEWS
        if not receivers:
            return

        news = News().get_important_news()
        for r in receivers:
            self.sendTextMsg(news, r)
