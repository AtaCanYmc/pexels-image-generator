from dotenv import load_dotenv
from pexels_api import API
import os
import requests
from pexels_api.tools import Photo
from utils.common_utils import get_remote_size, read_json_file, create_folders_if_not_exist

load_dotenv()

pexels_api_key = os.getenv('PEXELS_API_KEY')
if not pexels_api_key:
    raise EnvironmentError(
        "Environment variable `PEXELS_API_KEY` is not set. Set it in the environment or in a `.env` file.")
pexels_api = API(pexels_api_key)
max_image_kb = int(os.getenv('MAX_KB_IMAGE_SIZE', '512'))


def get_image_from_pexels(term, page_idx=1, results_per_page=15) -> list[Photo]:
    pexels_api.search(term, page=page_idx, results_per_page=results_per_page)
    photo_list = pexels_api.get_entries()
    return photo_list


def download_pexels_images(photo_list: list[Photo], folder_name: str):
    for photo in photo_list:
        url_list = [photo.original, photo.large2x, photo.large, photo.medium, photo.small]
        url_indx = 0
        content_kb = 0
        while url_indx < len(url_list):
            image_info = get_remote_size(url_list[url_indx])
            content_kb = image_info.get('kb_decimal', 0)
            if content_kb <= max_image_kb:
                break
            url_indx += 1
        image_data = requests.get(url_list[url_indx], timeout=30)
        image_path = os.path.join(folder_name, f"{photo.id}.{photo.extension}")
        with open(image_path, 'wb') as file:
            file.write(image_data.content)
        print(f"Downloaded image {photo.id} to {image_path} ({content_kb:.2f} KB)")


def ask_for_pexels_download(term: str, img: Photo) -> bool:
    while True:
        user_input = input(f"Download image {img.original} for term '{term}'? (y/n): ").strip().lower()
        if user_input in ['y', 'yes', '', ' '] or not user_input:
            return True
        elif user_input in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def convert_pexels_photo_to_json(img: Photo) -> dict:
    return {
        'id': img.id,
        'width': img.width,
        'height': img.height,
        'photographer': img.photographer,
        'url': img.url,
        'description': img.description,
        'original': img.original,
        'compressed': img.compressed,
        'large2x': img.large2x,
        'large': img.large,
        'medium': img.medium,
        'small': img.small,
        'portrait': img.portrait,
        'landscape': img.landscape,
        'tiny': img.tiny,
        'extension': img.extension,
        'apiType': 'pexels'
    }


def download_pexels_images_from_json(json_file: str, folder_name: str):
    data = read_json_file(json_file)
    for term, images in data.items():
        for img_data in images:
            if img_data.get('apiType') != 'pexels':
                continue

            url = img_data['original']
            image_info = get_remote_size(url)
            content_kb = image_info.get('kb_decimal', 0)

            if content_kb > max_image_kb:
                url = img_data['large2x']
                image_info = get_remote_size(url)
                content_kb = image_info.get('kb_decimal', 0)

            if content_kb > max_image_kb:
                url = img_data['large']
                image_info = get_remote_size(url)
                content_kb = image_info.get('kb_decimal', 0)

            if content_kb <= max_image_kb:
                image_data = requests.get(url, timeout=30)
                folder_path = os.path.join(folder_name, term)
                image_path = os.path.join(folder_path, f"{img_data['id']}.{img_data['extension']}")

                create_folders_if_not_exist([folder_path])
                with open(image_path, 'wb') as file:
                    file.write(image_data.content)
                print(f"Downloaded image {img_data['id']} to {image_path} ({content_kb:.2f} KB)")
            else:
                print(f"Skipped image {img_data['id']} ({content_kb:.2f} KB exceeds limit)")
