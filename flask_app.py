# python
import os
from flask import Flask, render_template_string, redirect, url_for, request
from pexels_api.tools import Photo
from utils.pexel_utils import convert_pexels_photo_to_json, get_image_from_pexels, download_pexels_images
from utils.common_utils import (create_folders_if_not_exist, read_search_terms,
                                get_yes_no_input, term_to_folder_name, project_name, read_html_as_string,
                                read_json_file, save_json_file, json_map_file_name, create_files_if_not_exist)

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
search_terms = read_search_terms(search_file_path)

state = {
    "term_idx": 0,
    "photo_idx": 0,
    "photos_cache": {},  # term_idx -> list[Photo]
    "downloaded": 0,
    "downloaded_json": read_json_file(json_file_path),
}

TEMPLATE = read_html_as_string("templates/home_page.html")


def get_photos_for_term_idx(idx):
    if idx in state["photos_cache"]:
        return state["photos_cache"][idx]
    if idx < 0 or idx >= len(search_terms):
        return []
    term = search_terms[idx]
    photos = get_image_from_pexels(term, page_idx=1, results_per_page=15) or []
    state["photos_cache"][idx] = photos
    return photos


def current_photo_info():
    ti = state["term_idx"]
    pi = state["photo_idx"]
    if ti >= len(search_terms):
        return None, None, None
    photos = get_photos_for_term_idx(ti)
    if not photos or pi >= len(photos):
        return search_terms[ti], None, None
    photo = photos[pi]
    # try common attributes
    url = getattr(photo, "large2x", None) or getattr(photo, "original", None)
    # fallback if object has src dict
    if not url:
        src = getattr(photo, "src", None)
        if isinstance(src, dict):
            url = src.get("large2x") or src.get("original") or next(iter(src.values()), None)
    return search_terms[ti], photo, url


def save_state_json():
    json_content = state["downloaded_json"]
    folder = f"assets/{project_name}/json_files"
    os.makedirs(folder, exist_ok=True)
    json_path = os.path.join(folder, f"{json_map_file_name}.json")
    save_json_file(json_path, json_content)


def add_image_to_json(term: str, img: Photo):
    json_state = state["downloaded_json"]
    trm = term_to_folder_name(term)
    image_list = json_state.get(trm, [])

    if trm not in json_state:
        json_state[trm] = []

    if img.id not in [image['id'] for image in image_list]:
        json_state[trm].append(convert_pexels_photo_to_json(img))
        save_state_json()


def advance_after_action():
    # ilerle: aynı terimde bir sonraki foto, biterse bir sonraki terime geç
    state["photo_idx"] += 1
    photos = get_photos_for_term_idx(state["term_idx"])
    if state["photo_idx"] >= len(photos):
        state["term_idx"] += 1
        state["photo_idx"] = 0


@app.route("/")
def index():
    if state["term_idx"] >= len(search_terms):
        return render_template_string(TEMPLATE, finished=True, downloaded=state["downloaded"])
    term, photo, url = current_photo_info()
    finished = False
    if term is None:
        finished = True
    return render_template_string(
        TEMPLATE,
        finished=finished,
        term=term,
        term_idx=state["term_idx"],
        total_terms=len(search_terms),
        photo_url=url,
        downloaded=state["downloaded"]
    )


@app.route("/decision", methods=["POST"])
def decision():
    action = request.form.get("action")
    term, photo, url = current_photo_info()
    if not term:
        return redirect(url_for("index"))
    if action == "next":
        # sadece terimi atla
        state["term_idx"] += 1
        state["photo_idx"] = 0
        return redirect(url_for("index"))
    if action == "yes" and photo:
        # hedef klasör
        folder = f"assets/{project_name}/image_files/{term_to_folder_name(term)}"
        os.makedirs(folder, exist_ok=True)
        # download_pexels_images beklenen argümanlara göre çağrılır
        download_pexels_images([photo], folder)
        add_image_to_json(term, photo)
        state["downloaded"] += 1
    # her iki durumda da ilerle
    advance_after_action()
    return redirect(url_for("index"))


@app.route("/next")
def next_step():
    advance_after_action()
    return redirect(url_for("index"))


if __name__ == "__main__":
    is_continue = get_yes_no_input(
        f"Fill the assets/{project_name}/search.txt file with search terms before continuing. Continue?")

    if not is_continue:
        print("Exiting program. Please fill the search.txt file and run again.")
        exit(0)

    app.run(host="0.0.0.0", port=8080, debug=True)
