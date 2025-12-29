import os
from dataclasses import dataclass, field
from typing import Optional, List

import requests
from dotenv import load_dotenv

from utils.common_utils import get_remote_size

load_dotenv()

unsplash_api_url = os.getenv("UNSPLASH_API_URL", "https://api.unsplash.com")
unsplash_api_key = os.getenv('UNSPLASH_API_KEY')
if not unsplash_api_key:
    raise EnvironmentError(
        "Environment variable `UNSPLASH_API_KEY` is not set. Set it in the environment or in a `.env` file.")


@dataclass
class Urls:
    raw: Optional[str] = None
    full: Optional[str] = None
    regular: Optional[str] = None
    small: Optional[str] = None
    thumb: Optional[str] = None
    small_s3: Optional[str] = None


@dataclass
class ProfileImage:
    small: Optional[str] = None
    medium: Optional[str] = None
    large: Optional[str] = None


@dataclass
class UserLinks:
    self_: Optional[str] = None
    html: Optional[str] = None
    photos: Optional[str] = None


@dataclass
class User:
    id: str
    username: str
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    instagram_username: Optional[str] = None
    twitter_username: Optional[str] = None
    portfolio_url: Optional[str] = None
    profile_image: Optional[ProfileImage] = None
    links: Optional[UserLinks] = None


@dataclass
class Links:
    self_: Optional[str] = None
    html: Optional[str] = None
    download: Optional[str] = None


@dataclass
class UnsplashImage:
    id: str
    created_at: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    color: Optional[str] = None
    blur_hash: Optional[str] = None
    description: Optional[str] = None
    alt_description: Optional[str] = None
    urls: Optional[Urls] = None
    links: Optional[Links] = None
    user: Optional[User] = None
    current_user_collections: List[dict] = field(default_factory=list)


def remove_id_from_img_url(url: str) -> str:
    if url.find('?ixid') != -1:
        parts = url.split('?ixid')
    else:
        parts = url.split('&ixid')
    return parts[0] if parts else url


def get_image_from_unsplash(query, limit=15) -> list[UnsplashImage]:
    url = f"{unsplash_api_url}/search/photos"
    params = {
        "query": query,
        "per_page": limit,
        "client_id": unsplash_api_key,
        "order_by": "relevant"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Hata oluştu: {response.status_code} - {response.text}")
        return []

    data = response.json()
    images = []

    for item in data['results']:
        img = UnsplashImage(
            id=item['id'],
            created_at=item.get('created_at'),
            width=item.get('width'),
            height=item.get('height'),
            color=item.get('color'),
            blur_hash=item.get('blur_hash'),
            description=item.get('description'),
            alt_description=item.get('alt_description'),
            urls=Urls(**item['urls']),
            links=Links(
                self_=item['links'].get('self'),
                html=item['links'].get('html'),
                download=item['links'].get('download')
            ),
            user=User(
                id=item['user']['id'],
                username=item['user']['username'],
                name=item['user'].get('name'),
                first_name=item['user'].get('first_name'),
                last_name=item['user'].get('last_name'),
                instagram_username=item['user'].get('instagram_username'),
                twitter_username=item['user'].get('twitter_username'),
                portfolio_url=item['user'].get('portfolio_url'),
                profile_image=ProfileImage(**item['user']['profile_image']),
                links=UserLinks(
                    self_=item['user']['links'].get('self'),
                    html=item['user']['links'].get('html'),
                    photos=item['user']['links'].get('photos')
                )
            ),
            current_user_collections=item.get('current_user_collections', [])
        )
        images.append(img)

    return images


def convert_unsplash_image_to_json(img: UnsplashImage) -> dict:
    return {
        'id': img.id,
        'created_at': img.created_at,
        'width': img.width,
        'height': img.height,
        'color': img.color,
        'blur_hash': img.blur_hash,
        'description': img.description,
        'alt_description': img.alt_description,
        'urls': {
            'raw': remove_id_from_img_url(img.urls.raw),
            'full': remove_id_from_img_url(img.urls.full),
            'regular': remove_id_from_img_url(img.urls.regular),
            'small': remove_id_from_img_url(img.urls.small),
            'thumb': remove_id_from_img_url(img.urls.thumb)
        },
        'links': {
            'self': img.links.self_,
            'html': img.links.html,
            'download': img.links.download
        },
        'user': {
            'id': img.user.id,
            'username': img.user.username,
            'name': img.user.name,
            'first_name': img.user.first_name,
            'last_name': img.user.last_name,
            'instagram_username': img.user.instagram_username,
            'twitter_username': img.user.twitter_username,
            'portfolio_url': img.user.portfolio_url,
            'profile_image': {
                'small': img.user.profile_image.small,
                'medium': img.user.profile_image.medium,
                'large': img.user.profile_image.large
            },
            'links': {
                'self': remove_id_from_img_url(img.user.links.self_),
                'html': remove_id_from_img_url(img.user.links.html),
                'photos': remove_id_from_img_url(img.user.links.photos)
            }
        },
        'current_user_collections': img.current_user_collections,
        'apiType': 'unsplash'
    }


def download_unsplash_images(image_list: list[UnsplashImage], folder_name: str):
    for img in image_list:
        url = remove_id_from_img_url(img.urls.full)
        image_info = get_remote_size(url)
        content_kb = image_info.get('kb_decimal', 0)
        if content_kb <= int(os.getenv('MAX_KB_IMAGE_SIZE', '512')):
            image_data = requests.get(url, timeout=30)
            extension = url.find('fm=') != -1 and url.split('fm=')[1].split('&')[0] or 'jpg'
            image_path = os.path.join(folder_name, f"{img.id}.{extension}")
            with open(image_path, 'wb') as file:
                file.write(image_data.content)
            print(f"Downloaded image {img.id} to {image_path} ({content_kb:.2f} KB)")
        else:
            print(f"Skipped image {img.id} ({content_kb:.2f} KB exceeds limit)")