from flask import Blueprint, render_template_string
from utils.common_utils import read_html_as_string
from utils.env_utils import get_env_file_as_kvp_list

settings_bp = Blueprint('settings', __name__)
SETTINGS_PAGE_HTML = read_html_as_string("templates/settings_page.html")


@settings_bp.route('/settings', methods=['GET', 'POST'])
def index():
    env_list = get_env_file_as_kvp_list(".env")
    return render_template_string(SETTINGS_PAGE_HTML, env_vars=env_list)
