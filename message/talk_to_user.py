from message.word_detect import *
import json

others_answer = json.load(open("./config.json", encoding='utf-8'))["others_answer"]
use_model = json.load(open("./config.json", encoding='utf-8'))["bot_set"]["use_model"]

def judge_res(msg, group_or_not):
    # --------------------------------------------------------------------------------------帮助页面
    res_flg = help_menu(msg)
    if res_flg[0]:
        return res_flg[1]
    # --------------------------------------------------------------------------------------发送涩图
    if group_or_not:
        # 发送不特别瑟瑟的
        res_flg = ghs_pic(msg)
        if res_flg[0]:
            return res_flg[1]
    else:
        # 发送瑟瑟的
        res_flg = hs_pic(msg)
        if res_flg[0]:
            return res_flg[1]
    # --------------------------------------------------------------------------------------古诗
    res_flg = gu_shi(msg)
    if res_flg[0]:
        return res_flg[1]
    # --------------------------------------------------------------------------------------音乐
    res_flg = get_music(msg)
    if res_flg[0]:
        return res_flg[1]
    # --------------------------------------------------------------------------------------图
    res_flg = api_pic(msg)
    if res_flg[0]:
        return res_flg[1]

    # --------------------------------------------------------------------------------------舔狗
    res_flg = get_dog(msg)
    if res_flg[0]:
        return res_flg[1]

    # --------------------------------------------------------------------------------------发送猫猫图
    res_flg = mao_pic(msg)
    if res_flg[0]:
        return res_flg[1]
    # --------------------------------------------------------------------------------------天气
    res_flg = get_weather(msg)
    if res_flg[0]:
        return res_flg[1]
    # --------------------------------------------------------------------------------------时间
    res_flg = get_time(msg)
    if res_flg[0]:
        return res_flg[1]
    return False


class Talk:
    def __init__(self, chatbot, ws):
        self.chatbot = chatbot
        self.ws = ws

    def talk_to_user(self, rev):  # 这里可以DIY对私聊yes酱的操作
        msg = rev["raw_message"]
        sender = rev['user_id']
        group_id = ""

        res_flg = judge_res(msg, False)

        if res_flg is False:
            if use_model:
                res_flg = self.chatbot.chat(msg)
                if res_flg[0]:
                    return res_flg[1]
                else:
                    return choice(others_answer["no_answer"])
            else:
                return choice(others_answer["no_answer"])

        else:
            return res_flg

    def talk_to_group_user(self, rev):  # 这里可以DIY对群聊中@yes酱的操作
        msg = rev["raw_message"]
        print("talk_to_group_user msg:", msg)
        sender = rev['user_id']
        group_id = rev["group_id"]

        res_flg = judge_res(msg, True)

        if res_flg is False:
            if use_model:
                res_flg = self.chatbot.chat(msg)
                if res_flg[0]:
                    return res_flg[1]
                else:
                    return choice(others_answer["no_answer"])
            else:
                return choice(others_answer["no_answer"])

        else:
            return res_flg

    # 对添加好友的操作
    def add_friends(self, rev):
        print(rev)
        sender = rev['user_id']
        msg = rev['comment'].split('回答:')[1]
        if_add = add_friend(sender, msg, self.ws)
        obj = {
            'isOK': if_add[0],
            'flag': rev['flag'],
            'friendsName': if_add[1]
        }
        return obj

    # # 这里可以DIY对群聊的操作
    # def group_action(self, rev):
    #     msg = rev["raw_message"]
    #     user_id = rev["user_id"]
    #     group_id = rev["group_id"]
    #     # --------------------------------------------------------------------------------------检测关键字禁言
    #     if_ban = detect_ban(msg, user_id, group_id, self.ws)
    #     if if_ban[0]:
    #         return if_ban[1]
    #     return choice(others_answer["no_answer"])
