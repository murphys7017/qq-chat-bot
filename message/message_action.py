import websockets
import json

configuration = json.load(open("./config.json", encoding='utf-8'))
group = configuration["bot_set"]["group"]


# 撤回消息
def delete_msg(msg_id, ws):
    data = {
        'message_id': msg_id
    }
    # cq_url = "ws://127.0.0.1:5700/set_group_ban"
    # requests.post(cq_url,data=data)
    action = "delete_msg"
    post_data = json.dumps({"action": action, "params": data})
    rev = ws.send(post_data)
    return [True, "不要说不该说的话啦~"]


# 禁言60s
def detect_ban(user_id, group_id, ws):
    if group_id not in group:
        return [False]
    data = {
        'user_id': user_id,
        'group_id': group_id,
        'duration': 60
    }
    # cq_url = "ws://127.0.0.1:5700/set_group_ban"
    # requests.post(cq_url,data=data)
    action = "set_group_ban"
    post_data = json.dumps({"action": action, "params": data})
    rev = ws.send(post_data)
    return [True, "不要说不该说的话啦~"]


# 发送消息
def send_message(msg, qq_id, ws, qq_type):
    if msg == "":
        return False
    if qq_type == "private":
        data = {
            'user_id': qq_id,
            'message': msg,
            'auto_escape': False
        }
        # cq_url = "ws://127.0.0.1:5700/send_private_msg"
        # with websockets.connect(cq_url) as websocket:
        # 	rev = websocket.send(json.dumps(data))
        action = "send_private_msg"
        post_data = json.dumps({"action": action, "params": data})
        # print(post_data)
        rev = ws.send(post_data)
    elif qq_type == "group":
        data = {
            'group_id': qq_id,
            'message': msg,
            'auto_escape': False
        }
        # cq_url = "ws://127.0.0.1:5700/send_group_msg"
        # with websockets.connect(cq_url) as websocket:
        # 	rev = websocket.send(json.dumps(data))
        action = "send_group_msg"
        post_data = json.dumps({"action": action, "params": data})
        rev = ws.send(post_data)
    elif qq_type == "friends":
        data = {
            'approve': msg['isOK'],
            'flag': msg['flag'],
            'remark': msg['friendsName']
        }
        action = "set_friend_add_request"
        post_data = json.dumps({"action": action, "params": data})
        rev = ws.send(post_data)
    else:
        return False
    # print(rev)
    if rev is None or rev['status'] == 'failed':
        return False
    else:
        # return ret['data']['message_id']
        # if json.loads(rev)['status'] == 'ok':
        return True
    return False
