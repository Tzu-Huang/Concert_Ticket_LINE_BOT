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



def show_image_locally(link):
    response = requests.get(link)
    img = PILImage.open(BytesIO(response.content))
    img.show()


img_url = "https://res.xinruipiao.com/2024/10-14/09/649371a67acbfface765e80d07fc539f.png"
show_image_locally(img_url)