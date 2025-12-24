from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend import models
from jinja2 import Environment, FileSystemLoader
import os

def debug_vocab():
    db = SessionLocal()
    try:
        print("Querying words...")
        words = db.query(models.Word).order_by(models.Word.created_at.desc()).all()
        print(f"Found {len(words)} words.")
        
        import sys
        sys.stdout.reconfigure(encoding='utf-8')
        for word in words:
            print(f"Word: {word.original_word}, Pron: {word.pronunciation}")

        print("Rendering template...")
        env = Environment(loader=FileSystemLoader('backend/templates'))
        template = env.get_template('vocabulary.html')
        
        # Mock request object since we don't have one
        rendered = template.render(request=None, words=words)
        print("Template rendered successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_vocab()
