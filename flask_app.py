# python
import os
import webbrowser
from threading import Timer
from typing import Any

from flask import Flask, render_template_string, redirect, url_for, request

from utils.flickr_utils import get_image_from_flickr, convert_flickr_image_to_json, download_flickr_images, \
    download_flicker_images_from_json
from utils.pexel_utils import convert_pexels_photo_to_json, get_image_from_pexels, download_pexels_images, \
    download_pexels_images_from_json
from utils.common_utils import (create_folders_if_not_exist, read_search_terms,
                                get_yes_no_input, term_to_folder_name, project_name, read_html_as_string,
                                read_json_file, save_json_file, json_map_file_name, create_files_if_not_exist,
                                min_image_for_term, is_download, save_text_file, app_port, app_host)
from utils.pixabay_utils import get_image_from_pixabay, convert_pixabay_image_to_json, download_pixabay_images, \
    download_pixabay_images_from_json
from utils.unsplash_utils import download_unsplash_images, convert_unsplash_image_to_json, get_image_from_unsplash, \
    remove_id_from_img_url, download_unsplash_images_from_json

app = Flask(__name__)

create_folders_if_not_exist([
    f"assets/{project_name}",
    f"assets/{project_name}/image_files",
    f"assets/{project_name}/json_files",
    f"assets/{project_name}/video_files",
])

create_files_if_not_exist([
    f"assets/{project_name}/search.txt",
    f"assets/{project_name}/json_files/{json_map_file_name}.json"
])

search_file_path = f"assets/{project_name}/search.txt"
json_file_path = f"assets/{project_name}/json_files/{json_map_file_name}.json"
json_map = read_json_file(json_file_path)

removed_keys = [key for key in json_map.keys() if len(json_map.get(key)) >= min_image_for_term] if json_map else []
search_terms = read_search_terms(search_file_path, removed_keys)

state = {
    "term_idx": 0,
    "photo_idx": 0,
    "photos_cache": {},  # term_idx -> list[Photo]
    "downloaded": 0,
    "downloaded_json": json_map,
    "current_api": 'pexels'
}

HOME_PAGE_HTML = read_html_as_string("templates/home_page.html")
TXT_SETUP_PAGE_HTML = read_html_as_string("templates/txt_setup_page.html")


def get_photos_for_term_idx(idx, use_cache=True) -> list[Any]:
    if idx < 0 or idx >= len(search_terms):
        return []

    if use_cache and idx in state["photos_cache"]:
        return state["photos_cache"][idx]
    else:
        state["photos_cache"][idx] = None

    api_type = state["current_api"]
    term = search_terms[idx]
    photos = []

    if api_type == 'pexels':
        photos = get_image_from_pexels(term, page_idx=1, results_per_page=30)
    elif api_type == 'pixabay':
        photos = get_image_from_pixabay(term, page_idx=1, results_per_page=30)
    elif api_type == 'unsplash':
        photos = get_image_from_unsplash(term, limit=30)
    elif api_type == 'flickr':
        photos = get_image_from_flickr(term, limit=30)

    state["photos_cache"][idx] = photos
    return photos


def current_photo_info():
    ti = state["term_idx"]
    pi = state["photo_idx"]
    cur_api = state["current_api"]
    cur_term = search_terms[ti]
    cur_term_saved_img_count = len(state["downloaded_json"].get(term_to_folder_name(cur_term), []))

    if ti >= len(search_terms):
        return None, None, None

    photos: Any = get_photos_for_term_idx(ti)

    if not photos or pi >= len(photos):
        return cur_term, None, None, None

    photo = photos[pi]
    url = None

    if cur_api == 'pixabay':
        url = photo.largeImageURL
        return cur_term, photo, url, cur_term_saved_img_count
    elif cur_api == 'pexels':
        url = getattr(photo, "large2x", None) or getattr(photo, "original", None)
    elif cur_api == 'unsplash':
        url = getattr(photo.urls, "full", None) or getattr(photo.urls, "regular", None)
        url = remove_id_from_img_url(url)
    elif cur_api == 'flickr':
        url = getattr(photo, 'hi_res_url', None) or getattr(photo, 'url', None)

    if not url:
        src = getattr(photo, "src", None)
        if isinstance(src, dict):
            url = src.get("large2x") or src.get("original") or next(iter(src.values()), None)
    return cur_term, photo, url, cur_term_saved_img_count


def save_state_json():
    json_content = state["downloaded_json"]
    folder = f"assets/{project_name}/json_files"
    os.makedirs(folder, exist_ok=True)
    json_path = os.path.join(folder, f"{json_map_file_name}.json")
    save_json_file(json_path, json_content)


def add_image_to_json(term: str, img: Any):
    c_api = state["current_api"]
    json_state = state["downloaded_json"]
    trm = term_to_folder_name(term)
    image_list = json_state.get(trm, [])

    if trm not in json_state:
        json_state[trm] = []

    if f"{img.id}-{c_api}" not in [f"{image['id']}-{c_api}" for image in image_list]:
        if c_api == 'pexels':
            json_state[trm].append(convert_pexels_photo_to_json(img))
        elif c_api == 'pixabay':
            json_state[trm].append(convert_pixabay_image_to_json(img))
        elif c_api == 'unsplash':
            json_state[trm].append(convert_unsplash_image_to_json(img))
        elif c_api == 'flickr':
            json_state[trm].append(convert_flickr_image_to_json(img))

        save_state_json()


def advance_after_action():
    state["photo_idx"] += 1
    photos = get_photos_for_term_idx(state["term_idx"])
    if state["photo_idx"] >= len(photos):
        state["term_idx"] += 1
        state["photo_idx"] = 0


def download_image(photo: Any, term: str, force_download=False):
    if not is_download and not force_download:
        return

    c_api = state["current_api"]
    folder = f"assets/{project_name}/image_files/{c_api}/{term_to_folder_name(term)}"
    os.makedirs(folder, exist_ok=True)

    if c_api == 'pixabay':
        download_pixabay_images([photo], folder)
    elif c_api == 'pexels':
        download_pexels_images([photo], folder)
    elif c_api == 'unsplash':
        download_unsplash_images([photo], folder)
    elif c_api == 'flickr':
        download_flickr_images([photo], folder)

    add_image_to_json(term, photo)
    state["downloaded"] += 1


def decision_execution(action: str):
    term, photo, url, cur_term_saved_img_count = current_photo_info()
    print(f"-> action: {action}")
    if not term:
        return redirect(url_for("review"))

    if action == "use-pexels-api":
        state["photos_cache"] = {}
        state["current_api"] = 'pexels'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)
        return redirect(url_for("review"))

    if action == "use-pixabay-api":
        state["photos_cache"] = {}
        state["current_api"] = 'pixabay'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)
        return redirect(url_for("review"))

    if action == "use-unsplash-api":
        state["photos_cache"] = {}
        state["current_api"] = 'unsplash'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)
        return redirect(url_for("review"))

    if action == "use-flickr-api":
        state["photos_cache"] = {}
        state["current_api"] = 'flickr'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)
        return redirect(url_for("review"))

    if action == "next-term":
        state["term_idx"] += 1
        state["photo_idx"] = 0
        return redirect(url_for("review"))

    if action == "prev-term":
        if state["term_idx"] > 0:
            state["term_idx"] -= 1
            state["photo_idx"] = 0
        return redirect(url_for("review"))

    if action == "previous":
        if state["photo_idx"] > 0:
            state["photo_idx"] -= 1
        elif state["term_idx"] > 0:
            state["term_idx"] -= 1
            prev_photos = get_photos_for_term_idx(state["term_idx"])
            state["photo_idx"] = max(0, len(prev_photos) - 1)
        return redirect(url_for("review"))

    if action == "yes" and photo:
        download_image(photo, term)
        advance_after_action()
        return redirect(url_for("review"))

    if action == "no":
        advance_after_action()
        return redirect(url_for("review"))

    return None


@app.route("/review")
def review():
    if not search_terms:
        return redirect(url_for("setup"))
    if state["term_idx"] >= len(search_terms):
        return render_template_string(HOME_PAGE_HTML, finished=True, downloaded=state["downloaded"])
    term, photo, url, cur_term_saved_img_count = current_photo_info()
    finished = False
    if term is None:
        finished = True
    return render_template_string(
        HOME_PAGE_HTML,
        finished=finished,
        term=term,
        term_idx=state["term_idx"],
        total_terms=len(search_terms),
        photo_url=url,
        downloaded=state["downloaded"],
        current_api=state["current_api"],
        term_photo_counter=cur_term_saved_img_count
    )


@app.route("/setup", methods=['GET', 'POST'])
def setup():
    global search_terms

    if request.method == 'POST':
        content = request.form.get('terms', '')
        save_text_file(search_file_path, content)
        search_terms = read_search_terms(search_file_path, removed_keys)
        return redirect(url_for("review"))

    return render_template_string(
        TXT_SETUP_PAGE_HTML,
        project_name=project_name,
        terms="\n".join(search_terms)
    )


@app.route("/<int:idx>")
def index_by_idx(idx):
    idx = int(idx) - 1
    if 0 <= idx < len(search_terms):
        state["term_idx"] = idx
        state["photo_idx"] = 0
    return redirect(url_for("review"))


@app.route("/decision", methods=["POST"])
def decision():
    action = request.form.get("action")
    return decision_execution(action)


@app.route("/download-api-images", methods=["POST"])
def download_api_images():
    if state["current_api"] == 'pexels':
        create_folders_if_not_exist([f"assets/{project_name}/image_files/pexels"])
        download_pexels_images_from_json(json_file_path, f"assets/{project_name}/image_files/pexels")
    elif state["current_api"] == 'pixabay':
        create_folders_if_not_exist([f"assets/{project_name}/image_files/pixabay"])
        download_pixabay_images_from_json(json_file_path, f"assets/{project_name}/image_files/pixabay")
    elif state["current_api"] == 'unsplash':
        create_folders_if_not_exist([f"assets/{project_name}/image_files/unsplash"])
        download_unsplash_images_from_json(json_file_path, f"assets/{project_name}/image_files/unsplash")
    elif state["current_api"] == 'flickr':
        create_folders_if_not_exist([f"assets/{project_name}/image_files/flickr"])
        download_flicker_images_from_json(json_file_path, f"assets/{project_name}/image_files/flickr")

    return redirect(url_for("review"))


def open_browser():
    url_host = app_host if app_host != '0.0.0.0' else 'localhost'
    webbrowser.open_new(f"http://{url_host}:{app_port}/setup")


if __name__ == "__main__":
    Timer(2, open_browser).start()
    app.run(host=app_host, port=app_port, debug=True, use_reloader=False)
