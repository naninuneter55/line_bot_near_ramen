from flask import Flask, request, abort
import os
import urllib
import requests

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, LocationMessage,
    CarouselTemplate, CarouselColumn, TemplateSendMessage, PostbackTemplateAction, MessageTemplateAction,
    URITemplateAction, StickerSendMessage, JoinEvent, LeaveEvent
)

app = Flask(__name__, static_url_path='/static')

line_bot_api = LineBotApi(os.environ.get("CHANNEL_ACCESS_TOKEN", "CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.environ.get("CHANNEL_SECRET", "CHANNEL_SECRET"))


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # handler.handle(body, signature)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="位置情報を送信してください"))

@handler.add(LeaveEvent)
def handle_leave(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="さようなら"))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location(event):
    latitude = event.message.latitude
    longitude = event.message.longitude
    url = "https://zunda-api.herokuapp.com/api/gnavi/search_rest"

    # latitude = 38.24866085616044
    # longitude = 140.89707255363464

    query = [
        ("latitude", latitude),
        ("longitude", longitude),
        # カレー
        # ("category_l", "RSFST16000"),
        # 居酒屋
        # ("category_l", "RSFST09000"),
        # ラーメン
        ("category_s", "RSFST08008"),
        # 和食
        # ("category_l", "RSFST01000"),
        ("range", 5),
        ("hit_per_page", 100),
    ]
    url += "?{0}".format(urllib.parse.urlencode(query))
    try:
        print(url)
        data = requests.get(url)
    except ValueError:
        print("APIアクセスに失敗しました。")
    result = data.json()['result']
    if 'rest' in result:
        reply_carousel(result, event)
    else:
        reply_not_found(event)


def reply_not_found(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="見つかりませんでした"))


def reply_carousel(result, event):
    rests = result['rest']
    print("### {} ###".format(len(rests)))
    cnt = 0
    c_cols = []
    for rest in rests:
        shop_image1 = rest['image_url']['shop_image1']
        NO_IMAGE = "https://ono-line-bot.herokuapp.com/static/images/no_image.png"
        if not shop_image1:
            shop_image1 = NO_IMAGE
        address = rest['address']
        tel = rest['tel']
        shop_url = rest['url']
        c_cols.append(CarouselColumn(
            thumbnail_image_url=shop_image1,
            title=rest['name'],
            text=(address[:57] + '...') if len(address) > 60 else address,
            actions=[
                URITemplateAction(
                    label=tel,
                    uri='tel:' + tel
                ),
                URITemplateAction(
                    label='ぐるなびで詳細を見る',
                    uri=shop_url
                ),
            ]
        ))
        cnt += 1
        if cnt == 5:
            break;

    try:
        carousel_template_message = TemplateSendMessage(
            alt_text='検索結果',
            template=CarouselTemplate(
                columns=c_cols
            )
        )
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message)
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)


if __name__ == "__main__":
    app.run(debug=True)
