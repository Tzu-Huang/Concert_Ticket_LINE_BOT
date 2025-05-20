from googleapiclient.discovery import build
from datetime import datetime
import re  # 加入正規表示法模組
from display_image import show_image_locally
from chatgpt_filter import choose_best_concert_info
import json
from dotenv import load_dotenv
import os
import cloudinary
import cloudinary.uploader
import requests

load_dotenv()  # 會讀取 .env 檔

# 現在你就可以安全地取得 API key 了：
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CX = os.getenv("CX")
API_KEY = os.getenv("API_KEY")

# ✅ 設定 Cloudinary 憑證
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ✅ 本地測試用
artists = ["蔡琴"]

# ✅ 儲存先前搜尋結果
last_results = {}

def upload_to_cloudinary(image_url):
    fallback_url = "https://drive.google.com/uc?export=view&id=1aIcG4dOEuNH6rnaRE95PQ-J4htAmtf08"

    try:
        resp = requests.get(image_url, timeout=6)
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"[❌] 圖片格式錯誤：{content_type}")
            return fallback_url

        upload_result = cloudinary.uploader.upload(resp.content, resource_type="image")
        uploaded_url = upload_result.get("secure_url")
        if not uploaded_url:
            print("[❌] Cloudinary 回傳空的網址")
            return fallback_url

        print(f"[✅] 上傳成功：{uploaded_url}")
        return uploaded_url

    except Exception as e:
        print(f"[❌] Cloudinary 上傳失敗：{e}")
        return fallback_url
    
def get_concerts_from_google(artist):
    service = build("customsearch", "v1", developerKey=API_KEY)
    current_year = datetime.now().year
    query = f"{artist} 台灣演唱會 {current_year} "

    res = service.cse().list(
        q=query,
        cx=CX,
        num=2
    ).execute()

    items = res.get("items", [])
    results = []
    for item in items:
        results.append({
            "title": item["title"],
            "link": item["link"],
            "snippet": item.get("snippet", "")
        })
    return results

def extract_information(text):
    date_match = re.search(r"(\d{4}[./年-]\d{1,2}[./月-]?\d{0,2})", text)
    location_match = re.search(r"(台北|台中|高雄|新北|桃園|台南|台灣|Taipei|Kaohsiung|Taichung)", text, re.IGNORECASE)
    return {
        "date": date_match.group(1) if date_match else "未知",
        "location": location_match.group(1) if location_match else "未知"
    }

def get_concert_details(artist):
    results = get_concerts_from_google(artist)
    concerts = []

    for item in results:
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        info = extract_information(title + " " + snippet)

        # 嘗試從 pagemap 拿圖片
        pagemap = item.get("pagemap", {})
        image_url = None
        if "cse_image" in pagemap and len(pagemap["cse_image"]) > 0:
            image_url = pagemap["cse_image"][0].get("src")

        # 如果主結果沒有圖片，就額外呼叫圖片搜尋 API
        if not image_url:
            image_url = search_concert_image(artist)

        concerts.append({
            "artist": artist,
            "title": title,
            "link": link,
            "snippet": snippet,
            "date": info["date"],
            "location": info["location"],
            "image": image_url
        })
    return concerts


def search_concert_image(artist):
    service = build("customsearch", "v1", developerKey=API_KEY)
    current_year = datetime.now().year
    query = f'{artist} 台灣演唱會 ({current_year}) ("宣傳海報" OR "台北站" OR "高雄站")'

    res = service.cse().list(
        q=query,
        cx=CX,
        searchType='image',
        num=1  # 只抓一張圖片
    ).execute()

    items = res.get("items", [])
    if items:
        return items[0].get("link", "（找不到圖片）")
    return "（找不到圖片）"

def check_updates():
    updated = False
    for artist in artists:
        print(f"\n🔍 正在搜尋演唱會資訊：{artist}")
        concerts = get_concert_details(artist)
        new_set = set([item["link"] for item in concerts])
        old_set = set([item["link"] for item in last_results.get(artist, [])])

        if new_set != old_set:
            print(f"✅ 找到 {artist} 的新演唱會資訊：")
            for event in concerts:
                print(f"""
==============================
🎤 歌手：{event['artist']}
📌 標題：{event['title']}
📅 日期：{event['date']}
📍 地點：{event['location']}
🔗 連結：{event['link']}
🖼️ 圖片：{event['image']}
==============================
""")
            last_results[artist] = concerts
            updated = True
            show_image_locally(event['image'])
        else:
            print(f"❌ 沒有新的演唱會資訊。")

    if not updated:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 所有歌手都沒有新演唱會資訊。")
# # 🔁 單次執行
# if __name__ == "__main__":
#     check_updates()

#     # ✅ 整理所有歌手的資訊（多筆候選資料）
#     concert_data = []
#     for artist in artists:
#         raw_data = get_concert_details(artist)
#         candidates = []
#         for item in raw_data:
#             candidates.append({
#                 "date": item["date"],
#                 "location": item["location"]
#             })
#         concert_data.append({
#             "artist": artist,
#             "candidates": candidates
#         })

#     # ✅ 呼叫 ChatGPT 判斷最準確的資訊
#     result = choose_best_concert_info(concert_data)

#     try:
#         filtered_results = json.loads(result)
#         print("\n🎯 最可信的演唱會資訊：\n")
#         for item in filtered_results:
#             print(f"🎤 {item['artist']}：{item['date']} @ {item['location']}")
#     except json.JSONDecodeError:
#         print("⚠️ ChatGPT 回傳的格式不是 JSON，原始回應如下：\n")
#         print(result)
def get_best_concert_info_for_line(artist):
    raw_data = get_concert_details(artist)

    candidates = []
    image_url = None
    link_url = None

    for item in raw_data:
        candidates.append({
            "date": item["date"],
            "location": item["location"]
        })
        if not image_url and item.get("image"):
            image_url = item["image"]
        if not link_url and item.get("link"):
            link_url = item["link"]

    concert_data = [{
        "artist": artist,
        "candidates": candidates
    }]

    result = choose_best_concert_info(concert_data)

    try:
        filtered_results = json.loads(result)
        final = filtered_results[0]

        # ✅ 上傳圖片至 Cloudinary
        image_url_uploaded = upload_to_cloudinary(image_url) if image_url else None
        
        if not image_url_uploaded:
            image_url_uploaded = "https://i.imgur.com/4AiXzf8.jpeg"
            print(f"[DEBUG] 原始圖片網址：{image_url}")
            print(f"[DEBUG] 上傳後 Cloudinary 圖片網址：{image_url_uploaded}")
        return {
            "artist": final["artist"],
            "date": final["date"],
            "location": final["location"],
            "image": image_url_uploaded,
            "link": link_url or "https://google.com"
        }
    except json.JSONDecodeError:
        return None

