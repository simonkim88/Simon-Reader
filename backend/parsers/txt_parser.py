import os
import html

def read_txt(file_path):
    try:
        encodings = ['utf-8', 'gb18030', 'shift_jis', 'euc-kr', 'latin-1']
        text = None
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    text = f.read()
                break # Success
            except UnicodeDecodeError:
                continue
                
        if text is None:
            print(f"Error reading TXT: Could not determine encoding for {file_path}")
            return None
            
        # Basic processing: split by double newlines to create paragraphs
        paragraphs = text.split('\n\n')
        
        # Wrap in HTML
        html_content = ""
        for p in paragraphs:
            if p.strip():
                # Escape HTML characters to prevent injection
                safe_text = html.escape(p.strip())
                # Convert single newlines to <br>
                safe_text = safe_text.replace('\n', '<br>')
                html_content += f"<p>{safe_text}</p>\n"
                
        return {
            'title': os.path.basename(file_path),
            'chapters': [{
                'id': 'chapter-1',
                'content': html_content,
                'href': 'chapter-1'
            }]
        }
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return None
