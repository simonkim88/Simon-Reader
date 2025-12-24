import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.parsers import epub_parser, docx_parser

class TestParsers(unittest.TestCase):

    @patch('backend.parsers.epub_parser.epub')
    def test_read_epub(self, mock_epub):
        # Mock the book object
        mock_book = MagicMock()
        mock_epub.read_epub.return_value = mock_book
        
        # Mock metadata
        mock_book.get_metadata.return_value = [('Test Book',)]
        
        # Mock items
        mock_item = MagicMock()
        mock_item.get_type.return_value = 9 # ebooklib.ITEM_DOCUMENT (usually 9)
        mock_item.get_content.return_value = b'<html><body><h1>Chapter 1</h1><p>Content</p></body></html>'
        mock_item.get_id.return_value = 'item1'
        mock_item.get_name.return_value = 'chapter1.html'
        
        mock_book.get_items.return_value = [mock_item]
        
        # Mock ebooklib constant since we might not have it installed in the test env perfectly or just to be safe
        with patch('backend.parsers.epub_parser.ebooklib') as mock_ebooklib:
            mock_ebooklib.ITEM_DOCUMENT = 9
            
            result = epub_parser.read_epub('dummy.epub')
            
            self.assertIsNotNone(result)
            self.assertEqual(result['title'], 'Test Book')
            self.assertEqual(len(result['chapters']), 1)
            self.assertIn('Chapter 1', result['chapters'][0]['content'])
            self.assertIn('Content', result['chapters'][0]['content'])

    @patch('backend.parsers.docx_parser.docx')
    def test_read_docx(self, mock_docx):
        # Mock document
        mock_doc = MagicMock()
        mock_docx.Document.return_value = mock_doc
        
        # Mock paragraphs
        p1 = MagicMock()
        p1.text = "Paragraph 1"
        p2 = MagicMock()
        p2.text = "Paragraph 2"
        
        mock_doc.paragraphs = [p1, p2]
        
        result = docx_parser.read_docx('dummy.docx')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Document')
        self.assertEqual(len(result['chapters']), 1)
        self.assertIn('<p>Paragraph 1</p>', result['chapters'][0]['content'])
        self.assertIn('<p>Paragraph 2</p>', result['chapters'][0]['content'])

if __name__ == '__main__':
    unittest.main()
