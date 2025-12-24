from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    file_path = Column(String, unique=True, index=True)
    file_type = Column(String) # 'epub' or 'docx'
    cover_image = Column(String, nullable=True)
    last_read_position = Column(String, nullable=True) # Store selector or scroll %
    created_at = Column(DateTime, default=datetime.utcnow)

class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    original_word = Column(String, index=True)
    translated_word = Column(String)
    pronunciation = Column(String, nullable=True)
    context_sentence = Column(Text, nullable=True)
    book_title = Column(String, nullable=True)
    language = Column(String) # 'en' or 'jp'
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    content = Column(Text)
    selected_text = Column(Text, nullable=True) # The text the comment is attached to
    cfi_range = Column(String, nullable=True) # For EPUB location
    created_at = Column(DateTime, default=datetime.utcnow)
    
    book = relationship("Book")

class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    cfi_range = Column(String) # Location in the book
    label = Column(String, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    book = relationship("Book")

class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    selected_text = Column(Text)
    cfi_range = Column(String) # Location
    color = Column(String, default="yellow")
    created_at = Column(DateTime, default=datetime.utcnow)

    book = relationship("Book")
