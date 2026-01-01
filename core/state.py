import os
from typing import Any

from utils.common_utils import (project_name, json_map_file_name, read_json_file,
                                save_json_file, min_image_for_term, read_search_terms)

search_file_path = f"assets/{project_name}/search.txt"
json_file_path = f"assets/{project_name}/json_files/{json_map_file_name}.json"

json_map = read_json_file(json_file_path)
removed_keys = [key for key in json_map.keys() if len(json_map.get(key)) >= min_image_for_term] if json_map else []
search_terms = read_search_terms(search_file_path, removed_keys)
downloaded_images_count = sum(len(v) for v in json_map.values()) if json_map else 0

state = {
    "term_idx": 0,
    "photo_idx": 0,
    "photos_cache": {},
    "downloaded": downloaded_images_count,
    "downloaded_json": json_map,
    "current_api": 'pexels'
}


def save_state_json():
    folder = f"assets/{project_name}/json_files"
    os.makedirs(folder, exist_ok=True)
    save_json_file(json_file_path, state["downloaded_json"])


def update_search_terms():
    global search_terms
    search_terms = read_search_terms(search_file_path, removed_keys)


def get_state_value(key: str) -> Any:
    return state.get(key, None)
