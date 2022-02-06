from message.message_action import *
from message.talk_to_user import *
import chat as chat
import datetime
import time
from threading import Thread

'''
private_msg 是对私聊消息的回复

group_msg 是对群聊消息的回复
    增加了管理员qq可以直接在群聊中控制 (admin_qq)

    
    增加了闲聊模式
        我想了想决定偷懒把加载放在这里

'''
configuration = json.load(open("./config.json", encoding='utf-8'))

bot_set = configuration["bot_set"]
detect_statement = configuration["detect_statement"]


def read_file():
    data = []
    with open("data/talk_data/specialQA", 'r', encoding='UTF-8') as f:
        for line in f.read().splitlines():
            temp = line.split("#@#")
            data.append(temp)
    return data


def another_thread(rev, ws, content, left):
    res = "[CQ:at,qq={}]".format(rev['user_id']) + ' ' + content
    time.sleep(left)
    send_message(res, rev["group_id"], ws, "group")
    return True


class MsgTalker:
    def __init__(self, ws):
        self.ws = ws
        self.talk_data = read_file()
        self.chat_model = False
        self.thread = []
        self.talk = Talk(chat, ws)

    def private_msg(self, rev):
        if rev["sub_type"] != "friend":
            return send_message('你还不是我的好友呀', rev['user_id'], self.ws, "private")

        return send_message(self.talk.talk_to_user(rev), rev["user_id"], self.ws, "private")

    # 启动一个线程并保存到   self.thread  中
    def remind(self, rev):
        msg = rev["raw_message"]
        for key in detect_statement["remind"]:
            if key in msg:
                try:
                    content = msg.split(key)[1]
                    time = msg.split(key)[0]
                    minute = 0
                    hour = time.split("点")[0]
                    hour = int(hour)
                    try:
                        minute = int(time.split("点")[1])
                        print(minute)
                    except:
                        if '分' in time:
                            minute = time.split("点")[1].split("分")[0]
                            minute = int(minute)

                    curr_time = datetime.datetime.now()
                    if curr_time.hour > hour:
                        send_message("时间不对啊", rev["group_id"], self.ws, "group")
                        return False
                    if curr_time.hour == hour:
                        if curr_time.minute > minute:
                            send_message("时间不对啊", rev["group_id"], self.ws, "group")
                            return False
                    left = (hour - curr_time.hour) * 60 * 60 + (minute - curr_time.minute) * 60
                    self.thread.append(Thread(target=another_thread, args=(rev, self.ws, content, left)))

                    for thr in self.thread:
                        if thr.isAlive():
                            pass
                        else:
                            thr.start()
                    return True
                except:
                    return False
            else:
                pass
        return False

    def group_msg(self, rev):
        # 查看是否有@自己的消息
        if "[CQ:at,qq={}]".format(bot_set["self_qq"]) in rev["raw_message"]:
            try:
                rev['raw_message'] = rev['raw_message'].split("] ")[1]
            except Exception as e:
                print(e)
                pass

            if rev['message'] == '[CQ:at,qq=2762018040] 开启闲聊模式':
                self.chat_model = True
                return send_message("我要开始犯傻说胡话啦~", rev["group_id"], self.ws, "group")
            elif rev['message'] == '[CQ:at,qq=2762018040] 关闭闲聊模式':
                self.chat_model = False
                return send_message("好吧，我闭嘴", rev["group_id"], self.ws, "group")

            if self.remind(rev):
                return send_message("好的，Alice知道了", rev["group_id"], self.ws, "group")

            # 管理员设置的一些远程命令
            if rev['user_id'] == bot_set["admin_qq"]:
                admin_cmd_path = configuration["admin_cmd_path"]

                if rev['message'] == '[CQ:at,qq=2762018040] 重启':
                    pass
                if rev['message'] == '[CQ:at,qq=2762018040] 关闭':
                    pass

            # 非远程指令和开启闲聊模式则进入talk_to_group_user命令列表
            return send_message(self.talk.talk_to_group_user(rev), rev["group_id"], self.ws, "group")

        # 闲聊
        if self.chat_model:
            try:
                rev['raw_message'] = rev['raw_message'].split("] ")[1]
                print(rev['raw_message'])
            except Exception as e:
                print(e)
                pass
            # 已经加载好的聊天机器人
            res = self.talk.talk_to_group_user(rev)

            return send_message(res, rev["group_id"], self.ws, "group")

        if rev['raw_message'] in bot_set["ban_words"]:
            if bot_set["ban_action"] == "禁言":
                detect_ban(rev["user_id"], rev["group_id"], self.ws)
            if bot_set["ban_action"] == "撤回":
                delete_msg(rev["message_id"], self.ws)

        return True

    def add_friends(self, rev):
        return send_message(self.talk.add_friends(rev), rev["user_id"], self.ws, "friends")

    def group_increase(self, rev):
        res = "[CQ:at,qq={}]".format(rev['user_id']) + ' ' + bot_set["group_increase_msg"]
        return send_message(res, rev["group_id"], self.ws, "group")

    def group_decrease(self, rev):
        res = "[CQ:at,qq={}]".format(rev['user_id']) + ' ' + bot_set["group_decrease_msg"]
        return send_message(res, rev["group_id"], self.ws, "group")
