from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('pbv6pKdGgkY7S2koXR+Db5mUGU7dhahKnUo0oR6KNEujbXWsMGef8Y4MRnZhGstD0P2x6frS1GE4CiXy75fEwFkyMCIfK8HH6z1nnmpPHhJxGN3/eEzb6U2g4mNs2wNzyoD7ZpD87U5b5dpMppWXkwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9d3dda483635f3e5373009df3f368011')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()

