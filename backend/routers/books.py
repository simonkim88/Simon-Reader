from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Book
from .. import models
import shutil
import os
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from ..parsers.epub_parser import extract_cover_image as extract_epub_cover
from ..parsers.docx_parser import extract_cover_image as extract_docx_cover
from ..parsers.pdf_parser import extract_cover_image as extract_pdf_cover

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

UPLOAD_DIR = "backend/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_class=HTMLResponse)
def get_books(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@router.post("/upload")
async def upload_book(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Check if file already exists in DB
    existing_book = db.query(models.Book).filter(models.Book.title == file.filename).first()
    if existing_book:
        raise HTTPException(status_code=400, detail="File already exists")

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Determine type
    file_type = "unknown"
    if file.filename.lower().endswith(".epub"):
        file_type = "epub"
    elif file.filename.lower().endswith(".docx"):
        file_type = "docx"
    elif file.filename.lower().endswith(".txt"):
        file_type = "txt"
    elif file.filename.lower().endswith(".pdf"):
        file_type = "pdf"
        
    # Create DB entry
    try:
        new_book = models.Book(
            title=file.filename,
            author="Unknown",
            file_path=file_path,
            file_type=file_type
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
    except Exception as e:
        # Cleanup file if DB insert fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Extract Cover Image (if applicable)
    try:
        cover_data = None
        content_type = None
        
        if file_type == "epub":
            cover_data, content_type = extract_epub_cover(file_path)
        elif file_type == "docx":
            cover_data, content_type = extract_docx_cover(file_path)
        elif file_type == "pdf":
            cover_data, content_type = extract_pdf_cover(file_path)
            
        if cover_data:
            # Save cover image to static/covers
            covers_dir = os.path.join("backend", "static", "covers")
            os.makedirs(covers_dir, exist_ok=True)
            
            # Determine extension
            ext = ".jpg"
            if content_type == "image/png": ext = ".png"
            elif content_type == "image/jpeg": ext = ".jpg"
            elif content_type == "image/gif": ext = ".gif"
            
            cover_filename = f"{new_book.id}{ext}"
            cover_path = os.path.join(covers_dir, cover_filename)
            
            with open(cover_path, "wb") as f:
                f.write(cover_data)
                
            # Update DB
            new_book.cover_image = f"/static/covers/{cover_filename}"
            db.commit()
            
    except Exception as e:
        print(f"Error extracting cover: {e}")
    
    return {"filename": file.filename, "id": new_book.id}

@router.delete("/highlights/{highlight_id}")
def delete_highlight(highlight_id: int, db: Session = Depends(get_db)):
    highlight = db.query(models.Highlight).filter(models.Highlight.id == highlight_id).first()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")
    db.delete(highlight)
    db.commit()
    return {"message": "Highlight deleted"}

@router.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: int, db: Session = Depends(get_db)):
    bookmark = db.query(models.Bookmark).filter(models.Bookmark.id == bookmark_id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return {"message": "Bookmark deleted"}

@router.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Delete file
    if os.path.exists(book.file_path):
        os.remove(book.file_path)
        
    db.delete(book)
    db.commit()
    return {"message": "Book deleted"}

class CommentCreate(BaseModel):
    content: str
    selected_text: str | None = None
    cfi_range: str | None = None

class BookmarkCreate(BaseModel):
    cfi_range: str
    label: str | None = None
    comment: str | None = None

@router.post("/{book_id}/comments")
def add_comment(book_id: int, comment: CommentCreate, db: Session = Depends(get_db)):
    db_comment = models.Comment(
        book_id=book_id,
        content=comment.content,
        selected_text=comment.selected_text,
        cfi_range=comment.cfi_range
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/{book_id}/comments")
def get_comments(book_id: int, db: Session = Depends(get_db)):
    return db.query(models.Comment).filter(models.Comment.book_id == book_id).all()

@router.post("/{book_id}/bookmarks")
def add_bookmark(book_id: int, bookmark: BookmarkCreate, db: Session = Depends(get_db)):
    db_bookmark = models.Bookmark(
        book_id=book_id,
        cfi_range=bookmark.cfi_range,
        label=bookmark.label,
        comment=bookmark.comment
    )
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark

@router.get("/{book_id}/bookmarks")
def get_bookmarks(book_id: int, db: Session = Depends(get_db)):
    return db.query(models.Bookmark).filter(models.Bookmark.book_id == book_id).all()

class HighlightCreate(BaseModel):
    selected_text: str
    cfi_range: str
    color: str = "yellow"

@router.post("/{book_id}/highlights")
def add_highlight(book_id: int, highlight: HighlightCreate, db: Session = Depends(get_db)):
    db_highlight = models.Highlight(
        book_id=book_id,
        selected_text=highlight.selected_text,
        cfi_range=highlight.cfi_range,
        color=highlight.color
    )
    db.add(db_highlight)
    db.commit()
    db.refresh(db_highlight)
    return db_highlight

@router.get("/{book_id}/highlights")
def get_highlights(book_id: int, db: Session = Depends(get_db)):
    return db.query(models.Highlight).filter(models.Highlight.book_id == book_id).all()

@router.get("/{book_id}/vocabulary")
def get_book_vocabulary(book_id: int, db: Session = Depends(get_db)):
    # 1. Get Book Title
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Ideally we should link Word to Book via ID, but current schema uses title.
    return db.query(models.Word).filter(models.Word.book_title == book.title).all()

class ProgressUpdate(BaseModel):
    position: str

@router.post("/{book_id}/progress")
def update_progress(book_id: int, progress: ProgressUpdate, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    book.last_read_position = progress.position
    db.commit()
    return {"message": "Progress saved"}

@router.post("/{book_id}/progress_beacon", status_code=204)
def update_progress_beacon(book_id: int, progress: ProgressUpdate, db: Session = Depends(get_db)):
    # Same as update_progress but simplified return for beacon
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if book:
        book.last_read_position = progress.position
        db.commit()
    return
