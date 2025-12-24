import pdfplumber
import os
import mimetypes
import html

def read_pdf(file_path, image_base_url=None):
    try:
        chapters = []
        full_text = ""
        
        with pdfplumber.open(file_path) as pdf:
            # For PDF, we'll treat the whole document as one chapter for now,
            # or we could split by pages. Let's do one chapter but with page breaks.
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    # Basic cleaning and formatting
                    # Split by newlines and wrap in paragraphs
                    paragraphs = text.split('\n')
                    for para in paragraphs:
                        if para.strip():
                            safe_text = html.escape(para.strip())
                            full_text += f"<p>{safe_text}</p>\n"
                
                # Add a page break indicator
                full_text += f"<hr class='page-break' data-page='{i+1}'>\n"

        chapters.append({
            'id': 'pdf-content',
            'content': full_text,
            'href': '#'
        })
        
        return {
            'title': os.path.basename(file_path),
            'chapters': chapters
        }
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_cover_image(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            if len(pdf.pages) > 0:
                first_page = pdf.pages[0]
                
                # Try to extract images from the first page
                if first_page.images:
                    # pdfplumber extracts image metadata. To get the actual image data,
                    # we might need to use the 'stream' object or crop the page.
                    # However, pdfplumber's image extraction can be complex.
                    # A simpler approach for cover is to render the first page as an image.
                    # But pdfplumber relies on other tools for rendering (like ImageMagick).
                    # Let's try to extract the raw image stream if possible.
                    
                    # Actually, pdfplumber provides access to the raw image data via 'stream'.
                    # Let's try to get the largest image on the first page.
                    
                    # Sort images by area (width * height) descending
                    sorted_images = sorted(first_page.images, key=lambda x: x['width'] * x['height'], reverse=True)
                    
                    if sorted_images:
                        img_obj = sorted_images[0]
                        # Accessing the raw stream might be tricky without deeper pdfminer access.
                        # Let's try a safer approach: Render the page to an image?
                        # pdfplumber.Page.to_image() requires Pillow and Ghostscript/ImageMagick usually.
                        # We have Pillow installed.
                        
                        try:
                            im = first_page.to_image(resolution=150)
                            # Convert to bytes
                            import io
                            img_byte_arr = io.BytesIO()
                            im.original.save(img_byte_arr, format='JPEG')
                            return img_byte_arr.getvalue(), 'image/jpeg'
                        except Exception as render_error:
                            print(f"Error rendering PDF page: {render_error}")
                            # Fallback: try to extract raw stream if possible (advanced)
                            pass
                            
        return None, None
    except Exception as e:
        print(f"Error extracting PDF cover: {e}")
        return None, None
