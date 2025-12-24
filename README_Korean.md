# Simon Reader

**Simon Reader**는 사용자가 외국어 서적(EPUB, DOCX)을 읽으며 어휘력을 향상시킬 수 있도록 돕는 웹 기반 전자책 리더 애플리케이션입니다.

## 🌟 주요 기능

*   **다양한 형식 지원**: EPUB 및 DOCX 형식의 전자책을 불러와 읽을 수 있습니다.
*   **단어 검색 및 번역**: 책을 읽으면서 모르는 단어를 클릭하면 Naver 사전 또는 StarDict를 통해 즉시 뜻을 확인할 수 있습니다.
*   **나만의 단어장**: 검색한 단어를 저장하여 나만의 단어장을 만들고 관리할 수 있습니다.
*   **하이라이트 및 북마크**: 중요한 문장을 형광펜으로 칠하거나(하이라이트), 읽던 위치를 북마크로 저장할 수 있습니다.
*   **독서 진행률 추적**: 각 책의 독서 진행 상황을 자동으로 저장하고 보여줍니다.

## 🛠 기술 스택

*   **Backend**: Python (FastAPI), SQLAlchemy (SQLite)
*   **Frontend**: HTML, CSS, JavaScript (Jinja2 Templates)
*   **Parser**: `ebooklib`, `beautifulsoup4`, `python-docx` (전자책 파싱)
*   **Etc**: `uvicorn` (서버 실행)

## 🚀 설치 및 실행 방법

이 프로젝트를 로컬 환경에서 실행하려면 다음 단계(Windows 기준)를 따르세요.

### 1. 환경 설정

Python(3.8 이상)과 Git이 설치되어 있어야 합니다.

```bash
# 저장소 복제 (Clone)
git clone https://github.com/simonkim88/Simon-Reader.git
cd Simon-Reader
```

### 2. 가상환경 생성 (선택 사항이지만 권장)

```bash
python -m venv venv
# 가상환경 활성화
.\venv\Scripts\activate
```

### 3. 라이브러리 설치

```bash
pip install -r backend/requirements.txt
```

### 4. 실행

프로젝트 루트 폴더에 있는 `run_app.bat` 파일을 더블 클릭하거나, 터미널에서 아래 명령어를 실행하세요.

```bash
./run_app.bat
```
또는
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 접속

웹 브라우저를 열고 `http://localhost:8000` 으로 접속하세요.

## 📁 폴더 구조

```
Simon-Reader/
├── backend/            # 백엔드 코드 (FastAPI)
│   ├── routers/        # API 라우터
│   ├── templates/      # HTML 템플릿
│   ├── static/         # 정적 파일 (CSS, JS)
│   ├── parsers/        # 전자책 파싱 로직
│   ├── database.py     # DB 연결 설정
│   ├── models.py       # DB 모델 정의
│   └── main.py         # 앱 진입점
├── simon_reader.db     # SQLite 데이터베이스 파일
└── run_app.bat         # 윈도우 실행 스크립트
```

## 📝 라이선스

이 프로젝트는 개인 학습 및 사용을 목적으로 만들어졌습니다.
