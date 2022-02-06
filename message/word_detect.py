import requests
import json
import os
from random import choice
from urllib.parse import quote
import datetime
import random
import urllib.request
import gzip

'''

'''
configuration = json.load(open("./config.json", encoding='utf-8'))

bot_set = configuration["bot_set"]
music_set = configuration["music_set"]
detect_statement = configuration["detect_statement"]

help_base = "这里是帮助菜单：\n"
help_base += "以下之类在非闲聊状态下均需要@Alice\n"
help_base += "1.私聊调教对话 例如aaa+bbb \n"
help_base += "      那么发送aaa就会返回bbb啦~\n"
help_base += "      可以发送rmaaa+bbb删除对话哦~\n"
help_base += "2.@murphy并说‘开启聊天模式’会激活聊天机器人聊天\n"
help_base += "      @murphy并说‘关闭聊天模式’会关闭聊天机器人聊天\n"
help_base += "3.发送这几个内容之一会获得一张涩图 [ "+",".join(detect_statement["ghs_pic"])+" ]\n"
help_base += "注：群内涩图和私聊涩图不同 \n"
help_base += "4.发送这几个内容之一会返回一句古诗 [ "+",".join(detect_statement["gu_shi"])+" ]\n"
help_base += "5.发送这几个内容之一会返回一句舔狗日记 [ "+",".join(detect_statement["get_dog"])+" ]\n"
help_base += "6.发送这几个内容之一会返回一张二次元图片 [ "+",".join(detect_statement["api_pic"])+" ]\n"
help_base += "7.发送这几个内容之一会返回一张猫猫表情 [ "+",".join(detect_statement["mao_pic"])+" ]\n"
help_base += "8.发送这几个内容之一会返回或者分享一首歌 [ "+",".join(detect_statement["get_music"])+" ]\n"
help_base += "9.发送这几个内容之一会返回当前时间 [ "+",".join(detect_statement["get_time"])+" ]\n"
help_base += "10.发送 地点+[ "+",".join(detect_statement["get_weather"])+" ] 返回天气\n"
help_base += "11.发送 [时间（例：3点10分 或3点 ps:没分也行）]+[" + ",".join(detect_statement["remind"])+"]+[要干啥]到了时间Alice会@你\n"
help_base += "另外，如果你说了不改说的话会根据管理员的设置撤回消息或者封禁60s\n"


# 获取重定向后的网址
def get_redirect_url(url):
    # 请求头，这里我设置了浏览器代理
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
    # 请求网页
    response = requests.get(url, headers=headers)
    print(response.url)  # 打印重定向后的网址
    # 返回重定向后的网址
    return response.url


# 帮助菜单
def help_menu(msg):
    if msg[:4] != "help":
        return [False]
    if msg == "help":
        return [True, help_base]


def add_data(msg, all_data):
    if msg.count("+") != 1:
        return [False]
    if "/" in msg or "|" in msg:
        return [True, "不能含有/或|呀~"]
    if msg.split("+")[1] == "":
        return [False]
    msg = msg.split("+")
    if len(msg[0]) < 1:
        return [True, "得有内容呀~"]
    for row in all_data:
        if msg[0] == row[0]:
            if msg[1] in row[1]:
                return [True, "这句话我已经会辣，不用再教我啦~"]
            row[1].append(msg[1])
            save_data(all_data)
            return [True, "Alice酱记住啦~"]
    all_data.append([msg[0], [msg[1]]])
    save_data(all_data)
    return [True, "Alice酱记住啦~"]


def save_data(all_data):
    with open("data/talk_data/specialQA", "a", encoding='UTF-8') as f:
        for row in all_data:
            temp = row[0] + "|" + "".join([i + "/" for i in row[1]])
            f.writelines(temp + "\n")


def del_data(del_data, all_data):
    if del_data[:2] != "rm":
        return [False]
    msg = del_data[2:].split("+")
    for i in range(len(all_data)):
        if msg[0] == all_data[i][0]:
            if len(all_data[i][1]) == 1:
                all_data.pop(i)
                save_data(all_data)
                return [True, "已经删除啦~"]
            all_data[i][1].remove(msg[1])
            save_data(all_data)
            return [True, "已经删除啦~"]
    return [True, "删除出错啦~"]


'''
原作者的api是从p站搞涩图，经常请求不到
原本想建个api的，但是涩图太色了，改本地了
然后我想了想应该分个级
    ghs_pic 涩图是那种没有什么漏点的不是特别色的，默认的直接发群里
    hs_pic 黄色是那种比较涩的，只能私聊获得
'''


def get_time(msg):
    if msg in detect_statement["get_time"]:
        curr_time = datetime.datetime.now()
        res = "现在是" + str(curr_time.year) + "年" + str(curr_time.month) + "月" + str(curr_time.day) + "日 \n" + str(
            curr_time.hour) + "点" + str(curr_time.minute) + "分"
        return [True, res]
    return [False]


def ghs_pic(msg):
    if msg in detect_statement["ghs_pic"]:
        setu_list = os.listdir(bot_set["ghs_pic_path"])
        local_img_url = "[CQ:image,file=file:///" + bot_set["ghs_pic_path"] + choice(setu_list) + "]"
        return [True, local_img_url]
    return [False]


def hs_pic(msg):
    if msg in detect_statement["ghs_pic"]:
        setu_list = os.listdir(bot_set["hs_pic_path"])
        local_img_url = "[CQ:image,file=file:///" + bot_set["hs_pic_path"] + choice(setu_list) + "]"
        return [True, local_img_url]
    return [False]


def mao_pic(msg):
    if msg in detect_statement["mao_pic"]:
        setu_list = os.listdir(bot_set["mao_path"])
        local_img_url = "[CQ:image,file=file:///" + bot_set["mao_path"] + choice(setu_list) + "]"
        return [True, local_img_url]
    return [False]


# 古诗 ，来自今日诗词api
def gu_shi(msg):
    if msg in detect_statement["gu_shi"]:
        try:
            req_url = "https://v1.jinrishici.com/rensheng.txt"
            res = requests.get(req_url)
            print(res.text)
            return [True, res.text]
        except Exception as e:
            print(e)
            return [False, "阿这，出了一点问题"]
    return [False]


# 舔狗日记 ，来自今小歪api
def get_dog(msg):
    if msg in detect_statement["get_dog"]:
        try:
            req_url = "https://api.ixiaowai.cn/tgrj/index.php"
            print("请求数据 ...")
            res = requests.get(req_url)
            print(res.status_code)
            return [True, res.text]
        except Exception as e:
            print("请求数据失败")
            print(e)
            return [False, "阿这，出了一点问题"]
    return [False]


# 通过请求api获取图片
def api_pic(msg):
    if msg in detect_statement["api_pic"]:
        try:
            urls = ["https://api.ghser.com/random/api.php", "https://api.mz-moe.cn/img.php",
                    "https://api.ixiaowai.cn/api/api.php", "https://tenapi.cn/acg"]
            ret = random.randint(0, 3)
            res = get_redirect_url(urls[ret])
            local_img_url = "[CQ:image,file=" + res + "]"
            return [True, local_img_url]
        except Exception as e:
            print(e)
            return [False, "阿这，出了一点问题"]
    return [False]


def get_weather(msg):
    for get_weather in detect_statement["get_weather"]:
        if msg[-len(get_weather):] == get_weather:
            url1 = 'http://wthrcdn.etouch.cn/weather_mini?city=' + urllib.parse.quote(msg[:-len(get_weather)])
            weather_data = urllib.request.urlopen(url1).read()
            weather_data = gzip.decompress(weather_data).decode('utf-8')
            weather_dict = json.loads(weather_data)
            if weather_dict.get('desc') == 'invilad-citykey':
                res = '你输入的城市名有误，或者天气中心未收录你所在城市，不过八成是你输入的格式错了'
                return [True, res]
            elif weather_dict.get('desc') == 'OK':
                forecast = weather_dict.get('data').get('forecast')
                res = "------天气查询------ \n"
                res += "城市：" + weather_dict.get('data').get('city') + " \n"
                res += "温度：" + weather_dict.get('data').get('wendu') + "℃ " + " \n"
                res += "感冒：" + weather_dict.get('data').get('ganmao') + " \n"
                res += "风向：" + forecast[0].get('fengxiang') + " \n"
                res += "风级：" + forecast[0].get('fengli') + " \n"
                res += "高温：" + forecast[0].get('high') + " \n"
                res += "低温：" + forecast[0].get('low') + " \n"
                res += "天气：" + forecast[0].get('type') + " \n"
                res += "日期：" + forecast[0].get('date') + " \n"
                res += "*******************************" + " \n"
                for i in range(1, 5):
                    res += '日期：' + forecast[i].get('date') + " \n"
                    res += '风向：' + forecast[i].get('fengxiang') + " \n"
                    res += '风级：' + forecast[i].get('fengli') + " \n"
                    res += '高温：' + forecast[i].get('high') + " \n"
                    res += '低温：' + forecast[i].get('low') + " \n"
                    res += '天气：' + forecast[i].get('type') + " \n"
                    res += '--------------------------' + " \n"
                return [True, res]
        else:
            pass
    return [False]


def get_music(msg):
    if msg in detect_statement["get_music"]:
        music_file_link = music_set["music_file_link"]
        if music_file_link is 0:
            try:
                req_url = "https://api.paugram.com/acgm/?list=1&play=true"
                res = get_redirect_url(req_url)
                print(res)
                return [True, res]
            except Exception as e:
                print(e)
                return [False, "阿这，出了一点问题"]
        elif music_file_link is 1:
            # [CQ:music,type=163,id=28949129]
            res = "[CQ:music,type=" + music_set["music_type"] + ",id=" + choice(music_set["musics"]) + "]"
            return [True, res]
    return [False]


def send_forward(msg, group_id, ws, sender):
    group_msg = []
    for item in msg:
        each_msg = {
            "type": "node",
            "data": {
                "name": "呜啦",
                "uin": bot_set["self_qq"],
                "content": item
            }
        }
        group_msg.append(each_msg)
    data = {
        'group_id': group_id,
        'messages': group_msg
    }
    # print(data)
    # cq_url = "ws://127.0.0.1:5700/send_group_forward_msg"
    # rev3 = requests.post(cq_url,data=data)
    # print(rev3.json())
    action = "send_group_forward_msg"
    post_data = json.dumps({"action": action, "params": data})
    rev = ws.send(post_data)
    # print(rev)
    returnStr = "[CQ:at,qq={sender}]".format(sender=sender)
    return returnStr


def send_private(msg, sender, ws):
    data = {
        'user_id': sender,
        'message': msg,
        'auto_escape': False
    }
    # cq_url = "ws://127.0.0.1:5700/send_private_msg"
    action = "send_private_msg"
    post_data = json.dumps({"action": action, "params": data})
    rev = ws.send(post_data)
    return rev


def add_friend(sender, msg, ws):
    # if sender in admin_qq:
    #     return [True, '']
    try:
        print('add_friends')
        if msg == 'Alice':
            return [True, ""]
        else:
            return [False, ""]
        # print(result)
        # if result != ():
        #     return [True, ""]
    except Exception as e:
        print(e)
    return [False, '']
