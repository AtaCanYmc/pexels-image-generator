from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os

from utils.common_utils import get_remote_size

load_dotenv()

scrapper_url = os.getenv('FLICKR_SCRAPPER_URL', 'https://www.flickr.com/search/')


@dataclass
class FlickerImage:
    id: str
    url: str
    hi_res_url: str


HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_image_from_flickr(query, limit=15) -> list[FlickerImage]:
    params = {
        "text": query,
        "license": "4,5,6,9,10"
    }

    r = requests.get(scrapper_url, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    images = set()

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue

        if "staticflickr.com" in src:
            hi_res = re.sub(r"_[a-z]\.jpg", "_b.jpg", src)
            images.add(FlickerImage(
                id=hi_res.split("/")[-1].split("_")[0],
                url=src,
                hi_res_url=hi_res
            ))

    return list(images)[:limit]


def convert_flickr_image_to_json(img: FlickerImage) -> dict:
    return {
        'id': img.id,
        'url': img.url,
        'highResUrl': img.hi_res_url,
        'apiType': 'flickr'
    }


def download_flickr_images(image_list: list[FlickerImage], folder_name: str):
    for img in image_list:
        url = img.hi_res_url
        image_info = get_remote_size(url)
        content_kb = image_info.get('kb_decimal', 0)
        if content_kb <= int(os.getenv('MAX_IMAGE_KB', '256')):
            image_data = requests.get(url, timeout=30)
            extension = url.split('.')[-1]
            image_path = os.path.join(folder_name, f"{img.id}.{extension}")
            with open(image_path, 'wb') as file:
                file.write(image_data.content)
            print(f"Downloaded image {img.id} to {image_path} ({content_kb:.2f} KB)")
