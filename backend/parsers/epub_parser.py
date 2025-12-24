import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import os
import mimetypes

def read_epub(file_path, image_base_url=None):
    try:
        book = epub.read_epub(file_path)
        chapters = []
        
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # Extract HTML content
                content = item.get_content().decode('utf-8')
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove existing scripts/styles to avoid conflicts
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Rewrite image URLs
                if image_base_url:
                    for img in soup.find_all('img'):
                        src = img.get('src')
                        if src:
                            # Handle relative paths if necessary, but usually just the filename or internal path
                            # EPUB internal paths can be tricky, but let's assume flat or simple relative for now.
                            # Better approach: resolve against item's path? 
                            # For now, let's just pass the raw src to the image endpoint and let it figure it out
                            # or just prepend the base url.
                            
                            # We need to make sure we don't break external links if any (unlikely in EPUB)
                            if not src.startswith('http'):
                                img['src'] = f"{image_base_url}/{src}"

                # Get body content
                body = soup.find('body')
                if body:
                    chapters.append({
                        'id': item.get_id(),
                        'content': str(body), # Return the inner HTML of body or the body tag itself
                        'href': item.get_name()
                    })
                    
        return {
            'title': book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else 'Unknown',
            'language': book.get_metadata('DC', 'language')[0][0] if book.get_metadata('DC', 'language') else 'en',
            'chapters': chapters
        }
    except Exception as e:
        print(f"Error reading EPUB: {e}")
        return None

def get_epub_image(file_path, image_path):
    try:
        book = epub.read_epub(file_path)
        # image_path might be relative like "../Images/cover.jpg" or just "cover.jpg"
        # We need to find the item in the book.
        
        # Normalize path separators
        image_path = image_path.replace('\\', '/')
        
        # Try exact match first
        for item in book.get_items():
            if item.get_name() == image_path:
                return item.get_content(), mimetypes.guess_type(image_path)[0]
        
        # Try matching by filename only if exact path fails (common in flat structures)
        filename = os.path.basename(image_path)
        for item in book.get_items():
            if os.path.basename(item.get_name()) == filename:
                 return item.get_content(), mimetypes.guess_type(filename)[0]
                 
        return None, None
    except Exception as e:
        print(f"Error extracting EPUB image: {e}")
        return None, None

def extract_cover_image(file_path):
    try:
        book = epub.read_epub(file_path)
        
        # 1. Try to find cover item from metadata (EPUB 2)
        # <meta name="cover" content="cover-image-id" />
        try:
            cover_metadata = book.get_metadata('OPF', 'cover')
            if cover_metadata:
                cover_id = cover_metadata[0][1].get('content')
                if cover_id:
                    item = book.get_item_with_id(cover_id)
                    if item:
                        return item.get_content(), mimetypes.guess_type(item.get_name())[0]
        except:
            pass

        # 2. Check for EPUB 3 'cover-image' property
        # Items in manifest can have properties="cover-image"
        # ebooklib items might have a 'properties' attribute (list)
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                if hasattr(item, 'properties') and 'cover-image' in item.properties:
                    return item.get_content(), mimetypes.guess_type(item.get_name())[0]

        # 3. Strict Heuristics (ID or Filename)
        images = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_IMAGE:
                images.append(item)
                
                # Check ID exactly
                if item.get_id().lower() == 'cover':
                    return item.get_content(), mimetypes.guess_type(item.get_name())[0]
                
                # Check Filename exactly (ignoring extension)
                name = os.path.basename(item.get_name()).lower()
                base_name = os.path.splitext(name)[0]
                if base_name == 'cover':
                    return item.get_content(), mimetypes.guess_type(item.get_name())[0]

        # 4. Check the first item in the spine (The "First Page")
        # Often the cover is the first thing shown, even if not marked in metadata
        if book.spine:
            try:
                # spine is list of (item_id, linear)
                first_spine_item = book.get_item_with_id(book.spine[0][0])
                if first_spine_item and first_spine_item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(first_spine_item.get_content(), 'html.parser')
                    
                    # Look for img tag
                    img_tag = soup.find('img')
                    if img_tag and img_tag.get('src'):
                        img_href = img_tag.get('src')
                        target_filename = os.path.basename(img_href)
                        for item in book.get_items():
                            if item.get_type() == ebooklib.ITEM_IMAGE:
                                if os.path.basename(item.get_name()) == target_filename:
                                    return item.get_content(), mimetypes.guess_type(item.get_name())[0]
                                    
                    # Look for SVG image (common in covers)
                    svg_image = soup.find('image')
                    if svg_image and svg_image.get('xlink:href'):
                        img_href = svg_image.get('xlink:href')
                        target_filename = os.path.basename(img_href)
                        for item in book.get_items():
                            if item.get_type() == ebooklib.ITEM_IMAGE:
                                if os.path.basename(item.get_name()) == target_filename:
                                    return item.get_content(), mimetypes.guess_type(item.get_name())[0]
            except Exception as e:
                print(f"Error checking spine for cover: {e}")

        # 5. Fallback: Iterate through SPINE to find the first image in reading order
        # This is much better than iterating get_items() which is arbitrary order
        for spine_id, linear in book.spine:
            try:
                item = book.get_item_with_id(spine_id)
                if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    
                    # Find first img
                    img_tag = soup.find('img')
                    if img_tag and img_tag.get('src'):
                        img_href = img_tag.get('src')
                        target_filename = os.path.basename(img_href)
                        
                        # Skip icons/logos if possible
                        if 'icon' in target_filename.lower() or 'logo' in target_filename.lower():
                            continue

                        for img_item in book.get_items():
                            if img_item.get_type() == ebooklib.ITEM_IMAGE:
                                if os.path.basename(img_item.get_name()) == target_filename:
                                    return img_item.get_content(), mimetypes.guess_type(img_item.get_name())[0]
            except:
                continue
            
        return None, None
        
    except Exception as e:
        print(f"Error extracting EPUB cover: {e}")
        return None, None


