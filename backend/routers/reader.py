from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Book
from ..parsers.epub_parser import read_epub, get_epub_image
from ..parsers.docx_parser import read_docx, get_docx_image
from ..parsers.txt_parser import read_txt
from ..parsers.pdf_parser import read_pdf
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/{book_id}")
def read_book(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    content = None
    image_base_url = f"/reader/{book_id}/images"
    
    if book.file_type == 'epub':
        content = read_epub(book.file_path, image_base_url)
    elif book.file_type == 'docx':
        content = read_docx(book.file_path, image_base_url)
    elif book.file_type == 'txt':
        content = read_txt(book.file_path)
    elif book.file_type == 'pdf':
        content = read_pdf(book.file_path, image_base_url)
    
    if not content:
        raise HTTPException(status_code=500, detail="Could not read book content")

    return templates.TemplateResponse("reader.html", {
        "request": request, 
        "book": book,
        "content": content
    })

@router.get("/{book_id}/images/{image_path:path}")
def get_book_image(book_id: int, image_path: str, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    image_data = None
    content_type = None
    
    if book.file_type == 'epub':
        image_data, content_type = get_epub_image(book.file_path, image_path)
    elif book.file_type == 'docx':
        image_data, content_type = get_docx_image(book.file_path, image_path)
        
    if image_data:
        return Response(content=image_data, media_type=content_type or "image/jpeg")
    
    raise HTTPException(status_code=404, detail="Image not found")

