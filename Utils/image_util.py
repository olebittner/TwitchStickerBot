import requests
from PIL import Image
import io


def download_image(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.content
    return False


def resize_image(image, size):
    img = Image.open(io.BytesIO(image))
    img = img.resize((size, size), resample=Image.LANCZOS)
    with io.BytesIO() as output:
        img.save(output, format="PNG")
        return output.getvalue()
