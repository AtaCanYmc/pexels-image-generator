from flask import Blueprint, request, redirect, url_for, render_template_string

from core.state import search_file_path, update_search_terms, search_terms
from utils.common_utils import read_html_as_string, save_text_file, project_name

setup_bp = Blueprint('setup', __name__)
TXT_SETUP_PAGE_HTML = read_html_as_string("templates/txt_setup_page.html")


@setup_bp.route("/setup", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('terms', '')
        save_text_file(search_file_path, content)
        update_search_terms()
        return redirect(url_for("review.index"))

    return render_template_string(
        TXT_SETUP_PAGE_HTML,
        project_name=project_name,
        terms="\n".join(search_terms)
    )
