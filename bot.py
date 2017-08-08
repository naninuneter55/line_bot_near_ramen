from flask import Flask, request, abort
import os
import urllib
import requests


from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN", "CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET", "CHANNEL_SECRET"))


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    handler.handle(body, signature)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("=== {} ===".format(event.message.text))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="あなたが言ったのは「" + event.message.text + "」"))


@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    msg = "今いるのは「" + event.message.address + "」緯度は「" + str(latitude) + "」経度は「" + str(longitude) + "」"
    print("=== {} ===".format(msg))
    url = "https://zunda-api.herokuapp.com/api/gnavi/search_rest"

    query = [
        ("latitude", latitude),
        ("longitude", longitude),
    ]
    url += "?{0}".format(urllib.parse.urlencode(query))
    try:
        data = requests.get(url)
    except ValueError:
        print("APIアクセスに失敗しました。")
    json = data.json()
    print("=== {} ===".format(len(json['result'])))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))


if __name__ == "__main__":
    app.run(debug=True)
