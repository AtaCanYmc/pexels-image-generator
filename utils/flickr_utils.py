from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import base64
from io import BytesIO
import json

from utils.common_utils import get_remote_size, term_to_folder_name, read_json_file

load_dotenv()

scrapper_url = os.getenv('FLICKR_SCRAPPER_URL', 'https://www.flickr.com/search/')


@dataclass
class FlickerImage:
    id: str
    url: str
    hi_res_url: str
    asset_path: str
    base64_data: str


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

    images = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if not src:
            continue

        if "staticflickr.com" in src:
            hi_res = re.sub(r"_[a-z]\.jpg", "_b.jpg", src)
            img_id = hi_res.split("/")[-1].split("_")[0]
            if any(existing_img.id == img_id for existing_img in images):
                continue
            images.append(FlickerImage(
                id=img_id,
                url=f"https:{src}",
                hi_res_url=f"https:{hi_res}",
                asset_path=f"{term_to_folder_name(query)}/{img_id}.jpg",
                base64_data=convert_image_to_base64(f"https:{hi_res}")
            ))

    return images[:limit]


def convert_flickr_image_to_json(img: FlickerImage) -> dict:
    return {
        'id': img.id,
        'url': img.url,
        'highResUrl': img.hi_res_url,
        'assetPath': img.asset_path,
        'base64Data': '',
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


def convert_image_to_base64(url: str) -> str:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    image_data = BytesIO(response.content)
    encoded_string = base64.b64encode(image_data.getvalue()).decode('utf-8')
    return encoded_string


def fix_asset_paths_of_json(json_file: str):
    image_list = read_json_file(json_file)
    for term, images in image_list.items():
        for img_data in images:
            if img_data.get('apiType') != 'flickr':
                continue

            if img_data.get('assetPath', None) is None:
                img_data['assetPath'] = f"{term_to_folder_name(term)}/{img_data['id']}.jpg"
                print(f"Fixed assetPath for {img_data['id']} to {img_data['assetPath']}")

    with open(json_file, 'w') as file:
        json.dump(image_list, file, indent=4)


def download_flicker_images_from_json(json_file: str, folder_name: str):
    image_list = read_json_file(json_file)
    for term, images in image_list.items():
        term_folder = os.path.join(folder_name, term_to_folder_name(term))
        img_types = set(img.get('apiType') for img in images)

        if not os.path.exists(term_folder) and 'flickr' in img_types:
            os.makedirs(term_folder)

        for img_data in images:
            if img_data.get('apiType') != 'flickr':
                continue

            img = FlickerImage(
                id=img_data['id'],
                url=img_data['url'],
                hi_res_url=img_data['highResUrl'],
                asset_path=img_data.get('assetPath', ''),
                base64_data=img_data.get('base64Data', '')
            )

            if img_data.get('assetPath', None) is None:
                print(f"Error at {img_data['id']} path is None")

            download_flickr_images([img], term_folder)
