import os
from dataclasses import dataclass
import requests
from utils.log_utils import logger
from dotenv import load_dotenv

load_dotenv()

wger_api_url = os.getenv("WGER_API_URL", "https://wger.de/api/v2")
wger_base_url = os.getenv('WGER_BASE_URL', "https://wger.de")


@dataclass
class WgerImage:
    id: int
    base_id: int
    value: str
    name: str
    category: str
    image: str
    image_thumbnail: str


def generate_search_url(term: str, limit=15, lang='en') -> str:
    return f"{wger_api_url}/exercise/search/?language={lang}&term={term}&limit={limit}"


def generate_exercise_image_url(exercise_id: int, licence_id=1) -> str:
    return f"{wger_api_url}/exerciseimage/?exercise={exercise_id}&license={licence_id}"


def convert_json_to_wger_image(json_data: dict) -> WgerImage:
    return WgerImage(
        value=json_data['value'],
        id=json_data['data']['id'],
        base_id=json_data['data']['baseId'],
        name=json_data['data']['name'],
        category=json_data['data']['category'],
        image=f"{wger_base_url}/{json_data['data']['image']}",
        image_thumbnail=f"{wger_base_url}/{json_data['data']['image_thumbnail']}",
    )


def convert_wger_image_to_json(img: WgerImage) -> dict:
    return {
        'id': img.id,
        'value': img.value,
        'base_id': img.base_id,
        'name': img.name,
        'category': img.category,
        'image': img.image,
        'image_thumbnail': img.image_thumbnail,
        'apiType': 'wger'
    }


def get_images_from_wger(term: str, limit=15, lang='en') -> list[WgerImage]:
    exercises = []
    url = generate_search_url(term, limit=limit, lang=lang)

    try:
        response = requests.get(url).json()
    except Exception as e:
        logger.error(f"Error fetching images from Wger for term '{term}': {e}")
        return []

    data = response['suggestions']

    for img in data:
        w_img = convert_json_to_wger_image(img)
        exercises.append(w_img)

    return exercises


def get_exercise_image(exercise_id):
    # License 1: Public Domain
    img_url = generate_exercise_image_url(exercise_id, licence_id=1)
    try:
        res = requests.get(img_url).json()
        if res['results']:
            return res['results'][0]['image']
    except Exception as e:
        logger.error(f"Error fetching images from Wger for exercise id '{exercise_id}': {e}")
        return None
