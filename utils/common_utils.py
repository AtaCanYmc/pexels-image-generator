import os
import random
import string
import requests
from dotenv import load_dotenv
import json

load_dotenv()

project_name = os.getenv('PROJECT_NAME', 'unknown')
json_map_file_name = os.getenv('IMAGE_MAP_JSON_NAME', 'downloaded_images')
min_image_for_term = int(os.getenv('MIN_IMAGES_PER_TERM', '1'))
is_download = os.getenv('DOWNLOAD_IMAGES', 'false').lower() == 'true'
app_port = os.getenv('APP_PORT', '8080')
app_host = os.getenv('APP_HOST', '0.0.0.0')


def generate_random_uuid() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))


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

    # Fallback: stream ile indirirken byte say (belleğe almadan)
    size = 0
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        for chunk in r.iter_content(8192):
            if chunk:
                size += len(chunk)

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


def copy_file_contents(src_path: str, dest_path: str):
    with open(src_path, 'r', encoding='utf-8') as src_file:
        content = src_file.read()
    with open(dest_path, 'w', encoding='utf-8') as dest_file:
        dest_file.write(content)


def generate_env_if_not_exist(env_path: str):
    example_env_path = env_path + '.example'
    if not os.path.exists(env_path):
        copy_file_contents(env_path, env_path)
