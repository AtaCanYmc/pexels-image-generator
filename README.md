# 📸 Media Reviewer Pro

Media Reviewer is a robust media procurement and curation tool built with Flask. It allows you to search, preview, and manage stock images from multiple APIs (Pexels, Pixabay, Unsplash, and Flickr) in one centralized workspace.



## 🚀 Key Features

* **Multi-API Integration:** Seamlessly fetch images from Pexels, Pixabay, Unsplash, and Flickr.
* **Smart Curation (Review Mode):** Quickly approve (✅) or reject (❌) images with real-time saving.
* **Dynamic Gallery:** Advanced filtering system by search terms, Image ID, or API source.
* **Asset Management:** Automated local storage of high-res images and one-click **ZIP** export.
* **Docker Ready:** Containerized environment for instant deployment without dependency issues.
* **Professional Logging:** Detailed system logs tracking downloads, deletions, and errors in the `logs/` directory.

---

## 🛠 Installation & Setup

### 1. Requirements
* **Docker & Docker Compose** (Recommended)
* OR **Python 3.10+**

### 2. Environment Variables (.env)
Create a `.env` file in the root directory and add your API keys:
```env
# API Keys
PEXELS_API_KEY=your_pexels_key
PIXABAY_API_KEY=your_pixabay_key
UNSPLASH_ACCESS_KEY=your_unsplash_key
FLICKR_API_KEY=your_flickr_key

# Project Configuration
PROJECT_NAME=my_project
APP_PORT=8080
DEBUG=True
DOWNLOAD_IMAGES=True
```

### 3. Running with Docker (Quickest)
```bash
  docker-compose up --build
```
Once started, visit http://localhost:8080 in your browser.

### 4. Manual Installation
```bash
    pip install -r requirements.txt
    python app.py
```

## 📂 Project Structure

The project follows a modular Blueprint architecture for better maintainability:

- **assets/:** Stores downloaded images and metadata (JSON files).
- **core/:** Contains centralized state management and core business logic.
- **routes/:** Modular page controllers (Gallery, Review, Setup, etc.).
- **utils/:** Utility scripts for API wrappers, logging, and file handling.
- **log_utils.py:** Custom logging system for file & console.
- **common_utils.py:** Shared file and URL helper functions.
- **logs/:** Auto-generated daily system logs.
- **templates/:** HTML5 templates styled with Tailwind CSS.
- **docker-compose.yml:** Orchestration for the containerized app.

## 📖 Usage Flow

1. **Step 1: Configuration & Setup** ⚙️
   * Enter your target keywords in the **Setup** page or edit `search.txt` directly.
   * Configure your API keys in the `.env` file to enable image fetching.

2. **Step 2: Curation & Review** ✅
   * Navigate to the **Review** tab to browse live photos from selected APIs.
   * Use the **Yes** button to approve and download, or **No** to skip.
   * Switch between different providers (Pexels, Pixabay, etc.) anytime during the session.

3. **Step 3: Management & Gallery** 🖼️
   * View all approved assets in the **Gallery**, automatically organized by search terms.
   * Use the **Dynamic Search Bar** to filter your collection by Image ID, source API, or term.
   * Delete unwanted images with the **Trash icon**; this removes the file from both your disk and the database.

4. **Step 4: Exporting Assets** 📦
   * Once your curation is complete, go to the **Project Assets** header.
   * Click **Download Project as ZIP** to get a structured archive containing all images and metadata JSONs.

## 🛡️ System Logging

The application implements a robust logging architecture to monitor background processes, API interactions, and file operations.

### 📝 Log Categories
* **Curation Actions:** Tracks every "Approve" or "Reject" decision with term and ID details.
* **API Events:** Logs requests to Pexels, Pixabay, Unsplash, and Flickr, including any rate-limiting or connection issues.
* **File Operations:** Monitors image downloads, ZIP creations, and permanent deletions from the disk.
* **Error Tracking:** Captures Python exceptions and Flask 500 errors with full context for easier debugging.

### 📂 Storage & Format
Logs are managed via `utils/log_utils.py` and stored in a structured format:
* **Console Output:** Real-time, color-coded feedback in your terminal or Docker dashboard.
* **Persistent Logs:** Saved daily in the `logs/` directory using the naming convention `app_YYYYMMDD.log`.

**Example Log Entry:**
`2026-01-02 00:15:48 | INFO | MediaReviewer | APPROVED: [toyota_corolla] - ID: 12345 - Source: pexels`