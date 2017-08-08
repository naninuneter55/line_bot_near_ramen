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
    MessageEvent, TextMessage, TextSendMessage, LocationMessage,
    CarouselTemplate, CarouselColumn, TemplateSendMessage, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
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


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     print("=== {} ===".format(event.message.text))
#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text="あなたが言ったのは「" + event.message.text + "」"))


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
        ("category_l", "RSFST16000"),
        ("range", 5)
    ]
    url += "?{0}".format(urllib.parse.urlencode(query))
    try:
        data = requests.get(url)
    except ValueError:
        print("APIアクセスに失敗しました。")
    json = data.json()
    rest_names = []
    rests = json['result']['rest']
    cnt = 0
    c_cols = []
    for rest in rests:
        rest_names.append(rest['name'])
        c_cols.append(CarouselColumn(
            thumbnail_image_url=rest['image_url']['shop_image1'],
            title=rest['name'],
            text=rest['name'],
            actions=[
                PostbackTemplateAction(
                    label='postback1',
                    text='postback text1',
                    data='action=buy&itemid=1'
                ),
                MessageTemplateAction(
                    label='message1',
                    text='message text1'
                ),
                URITemplateAction(
                    label='uri1',
                    uri='http://example.com/1'
                )
            ]
        ))
        cnt += 1
        if cnt == 5:
            break;

    msg = "\n".join(rest_names)
    print(">>> {} <<<".format(msg))
    print(">>> {} <<<".format(len(c_cols)))


    line_bot_api.reply_message(
        event.reply_token,
        TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(columns=c_cols)))
    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=msg))


if __name__ == "__main__":
    app.run(debug=True)
