import os
from typing import Any

from flask import Blueprint, redirect, url_for, render_template_string, request
from core.state import state, json_file_path, save_state_json, search_terms
from utils.common_utils import project_name, read_html_as_string, \
    term_to_folder_name, is_download, create_folders_if_not_exist
from utils.flickr_utils import get_image_from_flickr, convert_flickr_image_to_json, download_flickr_images, \
    download_flicker_images_from_json
from utils.pexel_utils import get_image_from_pexels, convert_pexels_photo_to_json, download_pexels_images, \
    download_pexels_images_from_json
from utils.pixabay_utils import get_image_from_pixabay, convert_pixabay_image_to_json, download_pixabay_images, \
    download_pixabay_images_from_json
from utils.unsplash_utils import get_image_from_unsplash, convert_unsplash_image_to_json, remove_id_from_img_url, \
    download_unsplash_images, download_unsplash_images_from_json

review_bp = Blueprint('review', __name__)
REVIEW_PAGE_HTML = read_html_as_string("templates/review_page.html")


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


def term_decision_execution(action: str):
    if action == "next-term":
        state["term_idx"] += 1
        state["photo_idx"] = 0

    if action == "prev-term":
        if state["term_idx"] > 0:
            state["term_idx"] -= 1
            state["photo_idx"] = 0

    return redirect(url_for("review.index"))


def decision_execution(action: str):
    term, photo, url, cur_term_saved_img_count = current_photo_info()
    print(f"-> action: {action} for term: {term}, photo idx: {photo}")
    if not term:
        return redirect(url_for("review.index"))

    if action == "previous":
        if state["photo_idx"] > 0:
            state["photo_idx"] -= 1
        elif state["term_idx"] > 0:
            state["term_idx"] -= 1
            prev_photos = get_photos_for_term_idx(state["term_idx"])
            state["photo_idx"] = max(0, len(prev_photos) - 1)
        return redirect(url_for("review.index"))

    if action == "yes" and photo:
        add_image_to_json(term, photo)
        state["downloaded"] += 1
        download_image(photo, term)
        advance_after_action()
        return redirect(url_for("review.index"))

    if action == "no":
        advance_after_action()
        return redirect(url_for("review.index"))

    return None


def api_decision_execution(action: str):
    if action == "use-pexels-api":
        state["photos_cache"] = {}
        state["current_api"] = 'pexels'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)

    if action == "use-pixabay-api":
        state["photos_cache"] = {}
        state["current_api"] = 'pixabay'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)

    if action == "use-unsplash-api":
        state["photos_cache"] = {}
        state["current_api"] = 'unsplash'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)

    if action == "use-flickr-api":
        state["photos_cache"] = {}
        state["current_api"] = 'flickr'
        state["photo_idx"] = 0
        get_photos_for_term_idx(state["term_idx"], use_cache=False)

    return redirect(url_for("review.index"))


@review_bp.route('/review')
def index():
    if not search_terms:
        return redirect(url_for("setup.index"))
    if state["term_idx"] >= len(search_terms):
        return render_template_string(REVIEW_PAGE_HTML, finished=True, downloaded=state["downloaded"])
    term, photo, url, cur_term_saved_img_count = current_photo_info()
    finished = False
    if term is None:
        finished = True
    return render_template_string(
        REVIEW_PAGE_HTML,
        finished=finished,
        term=term,
        term_idx=state["term_idx"],
        total_terms=len(search_terms),
        photo_url=url,
        downloaded=state["downloaded"],
        current_api=state["current_api"],
        term_photo_counter=cur_term_saved_img_count
    )


@review_bp.route("/review/<int:idx>")
def index_by_idx(idx):
    idx = int(idx) - 1
    if 0 <= idx < len(search_terms):
        state["term_idx"] = idx
        state["photo_idx"] = 0
    return redirect(url_for("review.index"))


@review_bp.route("/api-decision", methods=["POST"])
def api_decision():
    action = request.form.get("action")
    return api_decision_execution(action)


@review_bp.route("/term-decision", methods=["POST"])
def term_decision():
    action = request.form.get("action")
    return term_decision_execution(action)


@review_bp.route("/decision", methods=["POST"])
def decision():
    action = request.form.get("action")
    return decision_execution(action)


@review_bp.route("/download-api-images", methods=["POST"])
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

    return redirect(url_for("review.index"))
