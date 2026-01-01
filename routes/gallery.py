import json
import os
import shutil
from flask import Blueprint, render_template, request, redirect, url_for, send_file, render_template_string
from core.state import state, json_file_path
from utils.common_utils import project_name, read_json_file, save_json_file, get_image_url, get_thumbnail, \
    read_html_as_string

gallery_bp = Blueprint('gallery', __name__)
GALLERY_PAGE_HTML = read_html_as_string("templates/gallery_page.html")


@gallery_bp.route('/gallery')
def index():
    try:
        gallery_data = read_json_file(json_file_path)
    except (FileNotFoundError, json.JSONDecodeError):
        gallery_data = {}

    return render_template_string(GALLERY_PAGE_HTML,
                                  gallery_data=gallery_data,
                                  project_name=project_name,
                                  get_url_func=get_image_url,
                                  get_thumb_func=get_thumbnail)


@gallery_bp.route('/delete-image', methods=['POST'])
def delete_image():
    term = request.form.get('term')
    image_id = request.form.get('imageID')
    api_type = request.form.get('apiType')
    extension = request.form.get('extension', 'jpg')
    full_file_path = f"assets/{project_name}/image_files/{api_type}/{term}/{image_id}.{extension}"

    if os.path.exists(full_file_path):
        os.remove(full_file_path)

    try:
        image_list = read_json_file(json_file_path)
        images = image_list.get(term, [])
        image = next((img for img in images
                      if str(img.get('id')) == str(image_id)
                      and img.get('apiType') == api_type), None)
        if image:
            images.remove(image)
            image_list[term] = images
            save_json_file(json_file_path, image_list)

    except Exception as e:
        print(f"Delete Error: {e}")

    return redirect(url_for('gallery.index'))


@gallery_bp.route('/download-zip')
def download_zip():
    source_dir = f"assets/{project_name}"
    zip_filename = f"{project_name}_assets"
    zip_path = f"assets/{zip_filename}"

    if os.path.exists(source_dir):
        shutil.make_archive(zip_path, 'zip', source_dir)
        return send_file(f"{zip_path}.zip", as_attachment=True)
    else:
        return redirect(url_for("gallery.index"))

