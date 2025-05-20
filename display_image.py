import requests
from IPython.display import Image, display
from io import BytesIO
from PIL import Image as PILImage
from io import BytesIO
import requests

def display_image(link):
    try:
        response = requests.get(link, timeout=5)
        response.raise_for_status()  # Raise error if response is not 200 OK
        img_bytes = BytesIO(response.content)
        display(Image(data=img_bytes.read()))
    except Exception as e:
        print(f"❌ Error displaying image: {e}")



def show_image_locally(image_url):
    response = requests.get(image_url)

    # 檢查是否成功回傳圖片
    if response.status_code != 200:
        print(f"[ERROR] Failed to fetch image: {response.status_code}")
        return

    if 'image' not in response.headers.get('Content-Type', ''):
        print(f"[ERROR] URL does not point to an image: {response.headers.get('Content-Type')}")
        return

    # 正常讀取圖片
    img = PILImage.open(BytesIO(response.content))
    img.show()
