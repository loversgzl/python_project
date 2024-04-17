#python 3.8
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json

def GenSign():
    access_token = "ac7ca5cafebd83aae537f1167424302b5dfb0294a1a2ad127a0fb33e3e3302c7"
    secret = 'SEC2d7ccca82cb1a5396672f00536addfa1bac5067ecf6103f887b97ff6f5ea1c35'

    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

    url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token, timestamp, sign)
    return url

def send_dingding_message(webhook_url, content):
    headers = {
        'Content-Type': 'application/json',
    }

    # data = {
    #     'msgtype': 'text',
    #     "at": {"atMobiles":["16636122188"]},
    #     'text': {
    #         'content': content,
    #     }
    # }
    data = {
        'msgtype': 'markdown',
        "at": {"atMobiles":["16636122188"]},
        "markdown": {
         "title": "杭州天气",
         "text": "# 天气较冷，注意保暖 \n"
        }
    }

    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("消息发送成功")
    else:
        print(f"消息发送失败，错误码: {response.status_code}")


if __name__ == "__main__":
    # 替换为您自己的钉钉机器人Webhook地址
    webhook_url = GenSign()

    # 消息内容
    message_content = '测试'

    # 发送消息
    send_dingding_message(webhook_url, message_content)

