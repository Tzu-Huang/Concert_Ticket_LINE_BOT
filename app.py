from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
import os
from linebot.models import TextSendMessage, ImageSendMessage
from linebot.models import FlexSendMessage
import requests
from get_concert_from_google import get_best_concert_info_for_line  # 你自訂的方法

load_dotenv()

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except:
        abort(400)
    return 'OK'

def build_concert_flex(artist, date, location, image_url, link_url):
    flex_content = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": artist, "weight": "bold", "size": "xl"},
                {"type": "box", "layout": "baseline", "margin": "md", "contents": [
                    {"type": "text", "text": f"📅 {date}", "size": "sm", "color": "#999999"}
                ]},
                {"type": "box", "layout": "baseline", "margin": "sm", "contents": [
                    {"type": "text", "text": f"📍 {location}", "size": "sm", "color": "#999999"}
                ]}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "查看詳情",
                        "uri": link_url
                    }
                }
            ],
            "flex": 0
        }
    }
    return FlexSendMessage(alt_text=f"{artist} 演唱會資訊", contents=flex_content)

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    artist = event.message.text.strip()

    # 先回覆「查詢中...」
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"🔍 正在幫你搜尋「{artist}」的演唱會資訊...")
    )

    try:
        from get_concert_from_google import get_best_concert_info_for_line
        result = get_best_concert_info_for_line(artist)

        if result:
            flex = build_concert_flex(
                artist=result['artist'],
                date=result['date'],
                location=result['location'],
                image_url=result['image'],
                link_url=result['link']
            )
            line_bot_api.push_message(user_id, flex)
        else:
            line_bot_api.push_message(user_id, TextSendMessage(text="❌ 找不到演唱會資訊，請稍後再試。"))
    except Exception as e:
        line_bot_api.push_message(user_id, TextSendMessage(text=f"⚠️ 發生錯誤：{str(e)}"))

if __name__ == "__main__":
    app.run(port=8000)


