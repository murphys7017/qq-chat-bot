from message.message_action import *
from message.talk_to_user import *
import chat as chat
from message.function.RemindMe import *

'''
private_msg 是对私聊消息的回复

group_msg 是对群聊消息的回复
    增加了管理员qq可以直接在群聊中控制 (admin_qq)

    
    增加了闲聊模式
        我想了想决定偷懒把加载放在这里

'''

def read_file():
    data = []
    with open("data/talk_data/specialQA.txt", 'r', encoding='UTF-8') as f:
        for line in f.read().splitlines():
            temp = line.split("|")
            data.append(temp)
    return data

SPECIAL_ANSWER = []
SPECIAL_QUESTION = []

class MsgTalker:
    def __init__(self, ws, configuration):
        self.ws = ws
        self.talk_data = read_file()
        self.chat_group = False
        self.chat_private = False
        self.talk = Talk(chat, ws)
        self.remind = Remind(configuration, ws)
        self.bot_set = configuration["bot_set"]
        self.detect_statement = configuration["detect_statement"]
        for line in self.talk_data:
            SPECIAL_QUESTION.append(line[0])
            SPECIAL_ANSWER.append(line[1])

    def private_msg(self, rev):
        if rev["sub_type"] != "friend":
            return send_message('你还不是我的好友呀', rev['user_id'], self.ws, "private")
        msg = rev['raw_message']
        if SPECIAL_QUESTION.count(rev['raw_message']):
            text = SPECIAL_ANSWER[SPECIAL_QUESTION.index(rev['raw_message'])]
            return send_message(text, rev["user_id"], self.ws, "private")

        if rev["user_id"] in self.bot_set["admin_qq"]:
            if msg in self.detect_statement["chat_private_open"]:
                self.chat_private = True
                return send_message("我要开始犯傻说胡话啦~", rev["user_id"], self.ws, "private")
            elif msg in self.detect_statement["chat_private_stop"]:
                self.chat_private = False
                return send_message("好吧，我闭嘴", rev["user_id"], self.ws, "private")
            else:
                pass
        else:
            pass



        if msg[:2] == "每天":
            res = self.remind.remind_everyday(msg, rev['user_id'])
            if res[0]:
                return send_message("好的，Alice知道了,这是你的这个计划的id：" + res[1] + " ,用它来取消定时提醒", rev["user_id"], self.ws, "private")
        else:
            if self.remind.remind_do(rev['raw_message'], "", rev["user_id"]):
                return send_message("好的，Alice知道了", rev["user_id"], self.ws, "private")

        # 闲聊
        res = self.talk.talk_to_user(rev, self.chat_private)
        if res is not False:
            return send_message(res, rev["user_id"], self.ws, "private")
        

    def group_msg(self, rev):
        if SPECIAL_QUESTION.count(rev['raw_message']):
            text = SPECIAL_ANSWER[SPECIAL_QUESTION.index(rev['raw_message'])]
            return send_message(text, rev["group_id"], self.ws, "group")

        # 查看是否有@自己的消息
        if "[CQ:at,qq={}]".format(self.bot_set["self_qq"]) in rev["raw_message"]:
            try:
                rev['raw_message'] = rev['raw_message'].split("] ")[1]
            except Exception as e:
                pass

            if rev['raw_message'] in self.detect_statement["chat_group_open"]:
                self.chat_group = True
                return send_message("我要开始犯傻说胡话啦~", rev["group_id"], self.ws, "group")
            elif rev['raw_message'] in self.detect_statement["chat_group_stop"]:
                self.chat_group = False
                return send_message("好吧，我闭嘴", rev["group_id"], self.ws, "group")
            else:
                pass

            if self.remind.remind_do(rev['raw_message'], rev["group_id"], rev["user_id"]):
                return send_message("好的，Alice知道了", rev["group_id"], self.ws, "group")
            else:
                pass

            # 管理员设置的一些远程命令
            if rev['user_id'] == self.bot_set["admin_qq"]:
                
                if rev['raw_message'] == '重启':
                    pass
                if rev['raw_message'] == '关闭':
                    pass
            
            return send_message(self.talk.talk_to_group_user(rev, self.chat_group), rev["group_id"], self.ws, "group")

        if rev['raw_message'] in self.bot_set["ban_words"]:
            if self.bot_set["ban_action"] == "禁言":
                detect_ban(rev["user_id"], rev["group_id"], self.ws)
            if self.bot_set["ban_action"] == "撤回":
                delete_msg(rev["message_id"], self.ws)
        if  self.chat_group:
            return send_message(self.talk.talk_to_group_user(rev,self.chat_group), rev["group_id"], self.ws, "group")

    def add_friends(self, rev):
        return send_message(self.talk.add_friends(rev), rev["user_id"], self.ws, "friends")

    def group_increase(self, rev):
        res = "[CQ:at,qq={}]".format(rev['user_id']) + ' ' + self.bot_set["group_increase_msg"]
        return send_message(res, rev["group_id"], self.ws, "group")

    def group_decrease(self, rev):
        res = "[CQ:at,qq={}]".format(rev['user_id']) + ' ' + self.bot_set["group_decrease_msg"]
        return send_message(res, rev["group_id"], self.ws, "group")
