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
    URITemplateAction, StickerSendMessage
)

app = Flask(__name__, static_url_path='/static')

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
        print(">>> {} <<<".format(url))
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
        # c_cols.append(CarouselColumn(
        #     thumbnail_image_url=rest['image_url']['shop_image1'],
        #     title=rest['name'],
        #     text=rest['name'],
        #     actions=[
        #         # PostbackTemplateAction(
        #         #     label='postback1',
        #         #     text='postback text1',
        #         #     data='action=buy&itemid=1'
        #         # ),
        #         # MessageTemplateAction(
        #         #     label='message1',
        #         #     text='message text1'
        #         # ),
        #         URITemplateAction(
        #             label='uri1',
        #             uri='http://example.com/1'
        #         )
        #     ]
        # ))
        shop_image1 = rest['image_url']['shop_image1']
        print("###")
        print(type(shop_image1))
        print(shop_image1)
        print("###")
        NO_IMAGE = "https://ono-line-bot.herokuapp.com/static/images/no_image.png"
        if not shop_image1:
            print("#######################")
            shop_image1 = NO_IMAGE
        # print("%%% {} %%%".format(rest['image_url']))
        # print("%%% {} %%%".format(type(shop_image1)))
        # if shop_image1 is "":
        #     print("shop_image1 is \"\"")
        # if shop_image1 is None:
        #     print("shop_image1 is None")
        address = rest['address']
        tel = rest['tel']
        shop_url = rest['url']
        if shop_image1 is not NO_IMAGE:
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
        # c_cols.append(CarouselColumn(
        #     thumbnail_image_url='https://example.com/item1.jpg',
        #     title='this is menu1',
        #     text='description1',
        #     actions=[
        #         PostbackTemplateAction(
        #             label='postback1',
        #             text='postback text1',
        #             data='action=buy&itemid=1'
        #         ),
        #         MessageTemplateAction(
        #             label='message1',
        #             text='message text1'
        #         ),
        #         URITemplateAction(
        #             label='uri1',
        #             uri='http://example.com/1'
        #         )
        #     ]
        # ))


    msg = "\n".join(rest_names)
    print(">>> {} <<<".format(msg))
    print(">>> {} <<<".format(len(c_cols)))

    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=c_cols
            # columns=[
            #     CarouselColumn(
            #         thumbnail_image_url='https://example.com/item1.jpg',
            #         title='this is menu1',
            #         text='description1',
            #         actions=[
            #             PostbackTemplateAction(
            #                 label='postback1',
            #                 text='postback text1',
            #                 data='action=buy&itemid=1'
            #             ),
            #             MessageTemplateAction(
            #                 label='message1',
            #                 text='message text1'
            #             ),
            #             URITemplateAction(
            #                 label='uri1',
            #                 uri='http://example.com/1'
            #             )
            #         ]
            #     ),
            #     CarouselColumn(
            #         thumbnail_image_url='https://example.com/item2.jpg',
            #         title='this is menu2',
            #         text='description2',
            #         actions=[
            #             PostbackTemplateAction(
            #                 label='postback2',
            #                 text='postback text2',
            #                 data='action=buy&itemid=2'
            #             ),
            #             MessageTemplateAction(
            #                 label='message2',
            #                 text='message text2'
            #             ),
            #             URITemplateAction(
            #                 label='uri2',
            #                 uri='http://example.com/2'
            #             )
            #         ]
            #     )
            # ]
        )
    )

    try:
        line_bot_api.reply_message(
            event.reply_token,
            carousel_template_message)
    except LineBotApiError as e:
        print(e.status_code)
        print(e.error.message)
        print(e.error.details)

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TemplateSendMessage(
    #         alt_text='Carousel template',
    #         template=carousel_template_message))

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TemplateSendMessage(
    #         alt_text='Carousel template',
    #         template=CarouselTemplate(columns=c_cols)))

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     StickerSendMessage(
    #         package_id='1',
    #         sticker_id='1'
    #     ))

    # line_bot_api.reply_message(
    #     event.reply_token,
    #     TextSendMessage(text=msg))



if __name__ == "__main__":
    app.run(debug=True)
