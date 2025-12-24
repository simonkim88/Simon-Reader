from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from deep_translator import GoogleTranslator
from ..database import get_db
from .. import models
import requests
import re
from ..naver_scraper import scrape_naver_dict

import asyncio
from functools import partial
from ..stardict_manager import StarDictManager

router = APIRouter()

# Initialize StarDict Manager
stardict_manager = StarDictManager()

# Simple in-memory cache
WORD_CACHE = {}
CACHE_LIMIT = 1000

class WordCreate(BaseModel):
    original_word: str
    translated_word: str
    pronunciation: str | None = None
    context_sentence: str | None = None
    book_title: str | None = None
    language: str = "en"

from datetime import datetime

class WordResponse(WordCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

def contains_kana(text):
    # Check for Hiragana or Katakana
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text))

def contains_kanji(text):
    # Check for CJK Unified Ideographs
    return bool(re.search(r'[\u4E00-\u9FBF]', text))

# Translator Cache
TRANSLATOR_CACHE = {}

def get_translator(source="auto", target="ko"):
    key = f"{source}-{target}"
    if key not in TRANSLATOR_CACHE:
        TRANSLATOR_CACHE[key] = GoogleTranslator(source=source, target=target)
    return TRANSLATOR_CACHE[key]

@router.get("/lookup")
async def lookup_word(word: str, context: str | None = None, source: str = "auto", target: str = "ko"):
    # Check cache
    cache_key = f"{word}:{source}:{target}"
    if cache_key in WORD_CACHE:
        return WORD_CACHE[cache_key]

    definitions = []
    pronunciation = None
    
    try:
        # Determine language for Naver Dict
        lang = "en"
        
        # Prioritize explicit source
        if source == "ja":
            lang = "ja"
        elif source == "zh":
            lang = "zh"
        # Auto-detect fallback
        else:
            check_text = word + (context if context else "")
            if contains_kana(check_text):
                lang = "ja"
            elif contains_kanji(word):
                # If it has Kanji but no Kana (in word or context), assume Chinese
                lang = "zh"
        
        # Heuristic for sentence translation vs dictionary lookup
        # If text is long or has multiple spaces, treat as sentence/phrase -> use Google Translate directly
        if len(word) > 50 or word.count(' ') > 3:
             # Direct Translation (Skip Dictionary)
             def google_translate_direct():
                translator = get_translator(source=source, target=target)
                return translator.translate(word)
             
             translation = await asyncio.to_thread(google_translate_direct)
             return {"definitions": [translation] if translation else ["Translation failed."], "pronunciation": None, "examples": []}

        # 0. Try Local StarDict
        local_def = stardict_manager.lookup(word)
        if local_def:
            # StarDict definitions are often HTML or plain text.
            # We'll wrap it in a list to match the 'definitions' structure.
            # If it's very long, we might want to truncate or format it, but for now raw is fine.
            result = {"definitions": [local_def], "pronunciation": None}
            
            # Update Cache
            if len(WORD_CACHE) >= CACHE_LIMIT:
                WORD_CACHE.pop(next(iter(WORD_CACHE)))
            WORD_CACHE[cache_key] = result
            
            return result

        # 1. Try Naver Dictionary Scraping (Async)
        naver_result = await asyncio.to_thread(scrape_naver_dict, word, lang=lang)
        
        if naver_result:
            # Naver returns semicolon separated string, split it for frontend
            if "definition" in naver_result:
                definitions = [d.strip() for d in naver_result["definition"].split(";")]
            pronunciation = naver_result.get("pronunciation")
            examples = naver_result.get("examples", [])
            
            result = {"definitions": definitions, "pronunciation": pronunciation, "examples": examples}
            
            # Update Cache
            if len(WORD_CACHE) >= CACHE_LIMIT:
                WORD_CACHE.pop(next(iter(WORD_CACHE)))
            WORD_CACHE[cache_key] = result
            
            return result
            
        # 2. Fallback: Google Translator (if Naver fails) (Async)
        def google_translate():
            translator = get_translator(source=source, target=target)
            return translator.translate(word)

        translation = await asyncio.to_thread(google_translate)
        
        if translation:
            definitions.append(translation)
        
        # If it was English, try to get definitions from Free Dict API as well (legacy logic)
        if lang == "en":
             try:
                def fetch_free_dict():
                    api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
                    return requests.get(api_url, timeout=2)
                
                response = await asyncio.to_thread(fetch_free_dict)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        entry = data[0]
                        for meaning in entry.get("meanings", []):
                            for def_item in meaning.get("definitions", [])[:2]:
                                definitions.append(def_item.get('definition'))
             except:
                 pass

                 pass

        # Ensure examples key exists in fallback cases
        if "examples" not in locals():
            examples = []

        result = {"definitions": definitions, "pronunciation": pronunciation, "examples": examples}
        
        # Update Cache
        if len(WORD_CACHE) >= CACHE_LIMIT:
            WORD_CACHE.pop(next(iter(WORD_CACHE)))
        WORD_CACHE[cache_key] = result
        
        return result

    except Exception as e:
        print(f"Dictionary lookup error: {e}")
        # Ultimate Fallback
        try:
            def google_translate_fallback():
                translator = get_translator(source=source, target=target)
                return translator.translate(word)
                
            translation = await asyncio.to_thread(google_translate_fallback)
            return {"definitions": [translation], "pronunciation": None}
        except Exception as fallback_error:
            print(f"Fallback error: {fallback_error}")
            # Return a friendly error instead of 500
            return {"definitions": ["Could not find definition."], "pronunciation": None}

@router.post("/words", response_model=WordResponse)
def save_word(word: WordCreate, db: Session = Depends(get_db)):
    db_word = models.Word(
        original_word=word.original_word,
        translated_word=word.translated_word,
        pronunciation=word.pronunciation,
        context_sentence=word.context_sentence,
        book_title=word.book_title,
        language=word.language
    )
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

@router.get("/words", response_model=list[WordResponse])
def get_words(db: Session = Depends(get_db)):
    return db.query(models.Word).order_by(models.Word.created_at.desc()).all()

@router.delete("/words/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(models.Word).filter(models.Word.id == word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    db.delete(word)
    db.commit()
    return {"message": "Word deleted"}

import random

@router.get("/quiz")
def get_quiz_data(db: Session = Depends(get_db)):
    words = db.query(models.Word).all()
    
    if len(words) < 4:
        return {"error": "Not enough words. Please save at least 4 words to start a quiz."}
    
    # Select up to 10 random words for the quiz
    quiz_words = random.sample(words, min(len(words), 10))
    quiz_data = []
    
    for word in quiz_words:
        # Select 3 distractors
        distractors = random.sample([w for w in words if w.id != word.id], 3)
        options = [d.translated_word for d in distractors]
        options.append(word.translated_word)
        random.shuffle(options)
        
        quiz_data.append({
            "question": word.original_word,
            "options": options,
            "answer": word.translated_word,
            "pronunciation": word.pronunciation
        })
        
    return quiz_data

import csv
import io
from fastapi.responses import StreamingResponse

@router.get("/export")
def export_vocabulary(db: Session = Depends(get_db)):
    words = db.query(models.Word).order_by(models.Word.created_at.desc()).all()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['Word', 'Pronunciation', 'Translation', 'Context Sentence', 'Book Title', 'Date Added'])
    
    # Data
    for word in words:
        writer.writerow([
            word.original_word,
            word.pronunciation or '',
            word.translated_word,
            word.context_sentence or '',
            word.book_title or '',
            word.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output.seek(0)
    
    # Prepend BOM for Excel compatibility with UTF-8
    content = '\ufeff' + output.getvalue()
    
    response = StreamingResponse(iter([content]), media_type="text/csv; charset=utf-8")
    response.headers["Content-Disposition"] = "attachment; filename=vocabulary_export.csv"
    return response
