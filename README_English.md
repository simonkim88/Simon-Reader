# Simon Reader

**Simon Reader** is a web-based e-book reader application designed to help users improve their vocabulary while reading foreign language books (EPUB, DOCX).

## 🌟 Key Features

*   **Multi-Format Support**: Read e-books in EPUB and DOCX formats.
*   **Instant Word Lookup**: Click on unknown words while reading to instantly get definitions via Naver Dictionary or StarDict.
*   **Personal Vocabulary List**: Save searched words to build and manage your own vocabulary list.
*   **Highlights & Bookmarks**: Highlight important sentences and save your reading position with bookmarks.
*   **Reading Progress Tracking**: Automatically tracks and displays reading progress for each book.

## 🛠 Tech Stack

*   **Backend**: Python (FastAPI), SQLAlchemy (SQLite)
*   **Frontend**: HTML, CSS, JavaScript (Jinja2 Templates)
*   **Parser**: `ebooklib`, `beautifulsoup4`, `python-docx` (E-book parsing)
*   **Etc**: `uvicorn` (Server execution)

## 🚀 Installation & Usage

Follow these steps to run the project locally (Windows based).

### 1. Prerequisites

Ensure you have Python (3.8+) and Git installed.

```bash
# Clone the repository
git clone https://github.com/simonkim88/Simon-Reader.git
cd Simon-Reader
```

### 2. Set up Virtual Environment (Recommended)

```bash
python -m venv venv
# Activate virtual environment
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Run the Application

Double-click the `run_app.bat` file in the project root, or run the following command in the terminal:

```bash
./run_app.bat
```
Or:
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access

Open your web browser and go to `http://localhost:8000`.

## 📁 Project Structure

```
Simon-Reader/
├── backend/            # Backend code (FastAPI)
│   ├── routers/        # API routers
│   ├── templates/      # HTML templates
│   ├── static/         # Static files (CSS, JS)
│   ├── parsers/        # E-book parsers
│   ├── database.py     # Database connection setup
│   ├── models.py       # Database models
│   └── main.py         # Application entry point
├── simon_reader.db     # SQLite database file
└── run_app.bat         # Windows execution script
```

## 📝 License

This project is intended for personal learning and use.
