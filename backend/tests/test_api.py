from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import unittest
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.database import get_db, Base

# Mock DB
def override_get_db():
    try:
        db = MagicMock()
        yield db
    finally:
        pass

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAPI(unittest.TestCase):

    def test_lookup_word(self):
        with patch('backend.routers.dictionary.GoogleTranslator') as MockTranslator:
            instance = MockTranslator.return_value
            instance.translate.return_value = "사과"
            
            response = client.get("/dictionary/lookup?text=apple&source=en&target=ko")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"original": "apple", "translation": "사과"})

    def test_save_word(self):
        with patch('backend.routers.dictionary.get_db') as mock_db_dep:
            # We are mocking the dependency injection in the router
            # But TestClient uses the app's dependency_overrides.
            # So we need to ensure the db session mock behaves correctly.
            
            # Actually, since we overrode get_db globally for the app, 
            # the db session passed to save_word will be the MagicMock from override_get_db.
            # We just need to verify that db.add and db.commit are called.
            
            # However, verifying side effects on the dependency override mock is tricky 
            # because the generator yields a new mock each time or we need to control it.
            
            # Let's refine the override to return a specific mock we can check.
            mock_session = MagicMock()
            app.dependency_overrides[get_db] = lambda: mock_session
            
            word_data = {
                "original_word": "apple",
                "translated_word": "사과",
                "context_sentence": "I ate an apple.",
                "language": "en"
            }
            
            response = client.post("/dictionary/words", json=word_data)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["original_word"], "apple")
            
            mock_session.add.assert_called()
            mock_session.commit.assert_called()
            mock_session.refresh.assert_called()

    def test_add_comment(self):
        with patch('backend.routers.books.get_db') as mock_db_dep:
            mock_session = MagicMock()
            app.dependency_overrides[get_db] = lambda: mock_session
            
            comment_data = {
                "content": "This is a comment",
                "selected_text": "sample text",
                "cfi_range": "epubcfi(/6/4[chapter1]!/4/2)"
            }
            
            response = client.post("/books/1/comments", json=comment_data)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["content"], "This is a comment")
            
            mock_session.add.assert_called()
            mock_session.commit.assert_called()

    def test_add_bookmark(self):
        with patch('backend.routers.books.get_db') as mock_db_dep:
            mock_session = MagicMock()
            app.dependency_overrides[get_db] = lambda: mock_session
            
            bookmark_data = {
                "cfi_range": "epubcfi(/6/4[chapter1]!/4/2)",
                "label": "My Bookmark"
            }
            
            response = client.post("/books/1/bookmarks", json=bookmark_data)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["label"], "My Bookmark")
            
            mock_session.add.assert_called()
            mock_session.commit.assert_called()

if __name__ == '__main__':
    unittest.main()

