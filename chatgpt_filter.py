
import openai
import os

# ✅ 建立 OpenAI client（新版 API 寫法）
client = openai.OpenAI(api_key=openai_api_key)

def choose_best_concert_info(concert_data):
    messages = [
        {
            "role": "system",
            "content": (
                "你是一位專門協助判斷演唱會資訊真偽的助理。"
                "你將會收到每位歌手的多筆演唱會資料（日期與地點），"
                "請根據合理性、常見的演出慣例與資訊一致性，選出最有可能是正確的一筆。"
                "最後請為每位歌手各回傳一筆你認為最準確的資訊。"
                "請以 JSON 格式回傳，例如："
                "[{\"artist\": \"周杰倫\", \"date\": \"2024-11-03\", \"location\": \"台北\"}]"
            )
        },
        {
            "role": "user",
            "content": f"以下是演唱會資料：\n\n{concert_data}\n\n請回傳每位歌手最可能的日期與地點（使用 JSON 格式）"
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.2
    )

    return response.choices[0].message.content

