from flask import Flask, request, abort
import os

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
    print("=== {} ===".format(event.message.address))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="今いるのは「" + event.message.address + "」"))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="緯度は「" + event.message.latitude + "」"))
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="経度は「" + event.message.longitude + "」"))

if __name__ == "__main__":
    app.run(debug=True)
