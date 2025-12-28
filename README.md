# Pexels Reviewer

A simple Flask-based web UI to preview Pexels search results and save images based on Yes/No decisions.

## Features
1. Reads search terms from `assets/{project_name}/search.txt`.  
2. Shows preview images for each term from Pexels.  
3. If `Yes` is selected, the image is saved to `assets/{project_name}/image_files/<term>/` and metadata is recorded in `assets/{project_name}/json_files/downloaded_images.json`.  
4. Basic state management for progressing and skipping terms.

## Requirements
- Python 3.10+  
- Flask  
- Pexels API key (use a local ` .env` from ` .env.example`)

## Installation
1. Install dependencies:  
   `pip install -r requirements.txt`  
2. Copy the example env file and add your API keys locally (do not commit real keys):  
   `cp .env.example .env`  
3. Add search terms line-by-line to `assets/{project_name}/search.txt`.

## Usage
1. Run the development server:  
   `python flask_app.py`  
2. Open your browser at: `http://127.0.0.1:5000`

## Important files
- `flask_app.py` \- Flask application and workflow.  
- `templates/home_page.html` \- Web UI template.  
- `utils/pexel_utils.py` and `utils/common_utils.py` \- Pexels integration and helpers.  
- ` .env.example` \- Example environment variables (placeholders only).

## Notes
- Never commit real API keys to the repository.  
- Keep ` .env` local; commit only ` .env.example` with placeholder values.

## License
Add a suitable open source license (e.g. `LICENSE`) if required.