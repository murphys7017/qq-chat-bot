import websocket, time, json, logging
from massage_flide import MsgTalker

'''

这里是聊天机器人的启动函数
接收类似如下格式的数据：
        {
            'anonymous': None, 
            'font': 0, 
            'group_id': 345529951, 
            'message': '[CQ:at,qq=2762018040] 在？', 
            'message_id': -1608633614, 
            'message_seq': 48269, 
            'message_type': 'group', 
            'post_type': 'message', 
            'raw_message': '[CQ:at,qq=2762018040] 在？', 
            'self_id': 2762018040, 
            'sender': {'age': 0, 'area': '', 'card': '看到我请叫我去敲代码', 'level': '', 'nickname': '猫南北', 'role': 'admin', 'sex': 'unknown', 'title': '爱丽丝', 'user_id': 815049548}, 
            'sub_type': 'normal', 
            'time': 1643733237, 
            'user_id': 815049548
        }
        {
            'font': 0, 
            'message': '图', 
            'message_id': 1304589759, 
            'message_type': 'private', 
            'post_type': 'message', 
            'raw_message': '图', 
            'self_id': 2762018040, 
            'sender': {'age': 0, 'nickname': '猫南北', 'sex': 'unknown', 'user_id': 815049548}, 
            'sub_type': 'friend', 
            'target_id': 2762018040, 
            'time': 1645204890, 
            'user_id': 815049548
        }

'''
configuration = json.load(open("./config.json", encoding='utf-8'))

def recv_msg(_, message):
    try:
        rev = json.loads(message)
        # print(rev)
        if rev == None:
            # print('None.....')
            return False
        else:
            if rev["post_type"] == "message":
                # print(rev) #需要功能自己DIY
                if rev["message_type"] == "private":  # 私聊
                    talker.private_msg(rev)
                elif rev["message_type"] == "group":  # 群聊
                    if rev["group_id"] in configuration["bot_set"]["group"]:
                        talker.group_msg(rev)
                    else:
                        pass
                else:
                    pass
            elif rev["post_type"] == "notice":
                if rev["notice_type"] == "group_upload":  # 有人上传群文件
                    pass
                elif rev["notice_type"] == "group_decrease":  # 群成员减少
                    pass
                elif rev["notice_type"] == "group_increase":  # 群成员增加
                    talker.group_increase(rev)
                    pass
                else:
                    pass
            elif rev["post_type"] == "request":
                if rev["request_type"] == "friend":  # 添加好友请求
                    talker.add_friends(rev)
                    # pass
                if rev["request_type"] == "group":  # 加群请求
                    pass
            else:  # rev["post_type"]=="meta_event":
                pass
    except Exception as e:
        print(e)
        return False
        # continue
    # print(rev["post_type"])


ws_url = "ws://127.0.0.1:6700/ws"

ws = websocket.WebSocketApp(
    ws_url,
    on_message=recv_msg,
    on_open=lambda _: logger.debug('连接成功......'),
    on_close=lambda _: logger.debug('重连中......'),
)

talker = MsgTalker(ws,configuration)
print("Alice start now > <")

# 日志设置
logging.basicConfig(level=logging.DEBUG, format='[void] %(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    while True:
        ws.run_forever()
        time.sleep(1)
