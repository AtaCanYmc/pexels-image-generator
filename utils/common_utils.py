import os
import shutil
from threading import Timer
import requests
from dotenv import load_dotenv
import json
import uuid

from flask import send_file, Response

from utils.log_utils import logger

load_dotenv()

project_name = os.getenv('PROJECT_NAME', f'project_{str(uuid.uuid4())[:8]}')
json_map_file_name = os.getenv('IMAGE_MAP_JSON_NAME', 'downloaded_images')
min_image_for_term = int(os.getenv('MIN_IMAGES_PER_TERM', '1'))
is_download = os.getenv('DOWNLOAD_IMAGES', 'false').lower() == 'true'
app_port = os.getenv('APP_PORT', '8080')
app_host = os.getenv('APP_HOST', '0.0.0.0')
use_debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
use_reloader = os.getenv('USE_RELOADER', 'false').lower() == 'true'


def get_remote_size(url: str) -> dict:
    try:
        head = requests.head(url, timeout=10)
        cl = head.headers.get('Content-Length')
        if cl:
            size_bytes = int(cl)
            return {
                'bytes': size_bytes,
                'kb_decimal': size_bytes / 1000,
                'kb_binary': size_bytes / 1024,
                'source': 'Content-Length header'
            }
    except Exception:
        pass

    size = 0
    try:
        with requests.get(url, stream=True, timeout=30) as r:
            r.raise_for_status()
            for chunk in r.iter_content(8192):
                if chunk:
                    size += len(chunk)
    except Exception:
        print(f"Could not determine size for URL: {url}")  # Optional: log the error
        pass

    return {
        'bytes': size,
        'kb_decimal': size / 1000 if size > 0 else 0,
        'kb_binary': size / 1024 if size > 0 else 0,
        'source': 'streamed download'
    }


def term_to_folder_name(term: str) -> str:
    return term.replace(' ', '_').lower()


def create_folders_if_not_exist(folder_names: list[str]):
    for folder_name in folder_names:
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)


def create_files_if_not_exist(file_paths: list[str]):
    for file_path in file_paths:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')


def read_search_terms(file_path: str, remove_keys: list[str]) -> list[str]:
    with open(file_path, 'r') as file:
        terms = [line.strip() for line in file if line.strip()
                 and term_to_folder_name(line.strip()) not in remove_keys]
    return terms


def read_html_as_string(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_json_file(file_path: str, data: dict):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def save_text_file(file_path: str, data: str):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(data)


def delete_file_if_exists(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"Deleted file {file_path}")


def delete_files_if_exist(folder_path: str):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)


def get_project_folder_as_zip() -> tuple[Response, int]:
    source_dir = f"assets/{project_name}"
    zip_filename = f"{project_name}_assets"
    zip_path = f"assets/zip_files/{zip_filename}"

    shutil.make_archive(zip_path, 'zip', source_dir)
    # delete the zip file after 120 seconds
    Timer(120, delete_file_if_exists, args=[f"{zip_path}.zip"]).start()
    return send_file(f"{zip_path}.zip", as_attachment=True), 200


def get_image_url(img: dict) -> str:
    if not img:
        return "#"
    if img.get('apiType') == 'pexels':
        return img.get('original') or img.get('large2x') or img.get('url')
    elif img.get('apiType') == 'pixabay':
        return img.get('fullHDURL') or img.get('largeImageURL') or img.get('url')
    elif img.get('apiType') == 'unsplash':
        urls = img.get('urls', {})
        return urls.get('full') or urls.get('regular') or urls.get('small') or img.get('url')
    elif img.get('apiType') == 'flickr':
        return img.get('highResUrl') or img.get('url')
    return img.get('highResUrl') or img.get('original') or img.get('url') or "#"


def get_thumbnail(img):
    if img.get('apiType') == 'pexels':
        return img.get('tiny') or img.get('small')
    elif img.get('apiType') == 'pixabay':
        return img.get('previewURL')
    elif img.get('apiType') == 'unsplash':
        urls = img.get('urls', {})
        return urls.get('thumb') or urls.get('small')
    elif img.get('apiType') == 'flickr':
        return img.get('url')
    return '#'
