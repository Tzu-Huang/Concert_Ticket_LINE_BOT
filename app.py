from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
import os
import re
from linebot.models import TextSendMessage, ImageSendMessage
from linebot.models import FlexSendMessage
import requests
from get_concert_from_google import get_best_concert_info_for_line  # 你自訂的方法

load_dotenv()

app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.get("/health")
def health():
    return "OK", 200
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
    text = (event.message.text or "").strip()

    # 僅在「查詢 <藝人> 的演唱會」時觸發
    m = re.match(r'^查詢[\s　]+(.+?)[\s　]*的演唱會$', text)
    if not m:
        # 不符合格式：靜默忽略（或改成回傳指令說明）
        return

    artist = m.group(1)

    # 1) 先用 reply_token 回覆一次（只能一次）
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"🔎 已收到！正在搜尋「{artist}」的演唱會資訊…")
    )

    # 2) 查詢（可花較久時間），完了用 push 回傳結果
    try:
        from get_concert_from_google import get_best_concert_info_for_line
        result = get_best_concert_info_for_line(artist)

        if result:
            # 你自己的 Flex 產生器
            flex = build_concert_flex(
                artist=result.get('artist', artist),
                date=result.get('date', '日期未提供'),
                location=result.get('location', '地點未提供'),
                image_url=result.get('image', None),
                link_url=result.get('link', None),
            )
            line_bot_api.push_message(user_id, flex)
        else:
            line_bot_api.push_message(user_id, TextSendMessage(
                text=f"❌ 找不到「{artist}」的演唱會資訊，換個關鍵字再試試？"
            ))
    except Exception as e:
        print("concert query error:", e)
        line_bot_api.push_message(user_id, TextSendMessage(
            text="⚠️ 查詢時發生錯誤，稍後再試或換個藝人名稱。"
        ))

if __name__ == "__main__":
    app.run(port=8000)


