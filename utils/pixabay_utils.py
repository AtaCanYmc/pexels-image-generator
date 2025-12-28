import os
import requests
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

pixabay_api_key = os.getenv('PIXABAY_API_KEY')
pixabay_api_url = os.getenv('PIXABAY_API_URL')


@dataclass
class PixabayImage:
    id: int
    pageURL: str
    type: str
    tags: str
    previewURL: str
    previewWidth: int
    previewHeight: int
    webformatURL: str
    webformatWidth: int
    webformatHeight: int
    largeImageURL: str
    imageWidth: int
    imageHeight: int
    imageSize: int
    views: int
    downloads: int
    likes: int
    comments: int
    user_id: int
    user: str
    userImageURL: str


def get_image_from_pixabay(term, page_idx=1, results_per_page=15) -> list[PixabayImage]:
    params = {
        'key': pixabay_api_key,
        'q': term,
        'page': page_idx,
        'per_page': results_per_page,
        'image_type': 'photo',
    }
    response = requests.get(pixabay_api_url, params=params)
    data = response.json()
    image_list = []
    for item in data.get('hits', []):
        img = PixabayImage(
            id=item['id'],
            pageURL=item['pageURL'],
            type=item['type'],
            tags=item['tags'],
            previewURL=item['previewURL'],
            previewWidth=item['previewWidth'],
            previewHeight=item['previewHeight'],
            webformatURL=item['webformatURL'],
            webformatWidth=item['webformatWidth'],
            webformatHeight=item['webformatHeight'],
            largeImageURL=item['largeImageURL'],
            imageWidth=item['imageWidth'],
            imageHeight=item['imageHeight'],
            imageSize=item['imageSize'],
            views=item['views'],
            downloads=item['downloads'],
            likes=item['likes'],
            comments=item['comments'],
            user_id=item['user_id'],
            user=item['user'],
            userImageURL=item['userImageURL']
        )
        image_list.append(img)
    return image_list


def convert_pixabay_image_to_json(img: PixabayImage) -> dict:
    return {
        'id': img.id,
        'pageURL': img.pageURL,
        'type': img.type,
        'tags': img.tags,
        'previewURL': img.previewURL,
        'previewWidth': img.previewWidth,
        'previewHeight': img.previewHeight,
        'webformatURL': img.webformatURL,
        'webformatWidth': img.webformatWidth,
        'webformatHeight': img.webformatHeight,
        'largeImageURL': img.largeImageURL,
        'imageWidth': img.imageWidth,
        'imageHeight': img.imageHeight,
        'imageSize': img.imageSize,
        'views': img.views,
        'downloads': img.downloads,
        'likes': img.likes,
        'comments': img.comments,
        'user_id': img.user_id,
        'user': img.user,
        'userImageURL': img.userImageURL,
        'apiType': 'pixabay'
    }
