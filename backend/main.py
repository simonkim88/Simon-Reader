from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import get_db, engine
from . import models
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Simon-Reader API")

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

# Include Routers
from .routers import books, reader, dictionary
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(reader.router, prefix="/reader", tags=["reader"])
app.include_router(dictionary.router, prefix="/dictionary", tags=["dictionary"])

# CORS configuration
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root(request: Request, db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@app.get("/vocabulary")
def read_vocabulary(request: Request, db: Session = Depends(get_db)):
    words = db.query(models.Word).order_by(models.Word.created_at.desc()).all()
    books = db.query(models.Book).all()
    book_map = {b.title: b.id for b in books}
    return templates.TemplateResponse("vocabulary.html", {"request": request, "words": words, "book_map": book_map})

@app.get("/quiz")
def read_quiz(request: Request):
    return templates.TemplateResponse("quiz.html", {"request": request})

@app.get("/bookmarks")
def read_bookmarks(request: Request, db: Session = Depends(get_db)):
    bookmarks = db.query(models.Bookmark).order_by(models.Bookmark.created_at.desc()).all()
    return templates.TemplateResponse("bookmarks.html", {"request": request, "bookmarks": bookmarks})
