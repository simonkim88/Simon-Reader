from rembg import remove
from PIL import Image
import io

source_path = r"C:/Users/user/.gemini/antigravity/brain/ccee51dd-6565-4755-93a9-0cb0d0883a24/uploaded_image_1765360689609.png"
target_path = r"d:/Programing/Simon-Reader/backend/static/favicon.png"

try:
    print(f"Processing {source_path}...")
    with open(source_path, 'rb') as i:
        input_data = i.read()
        
    print("Removing background...")
    output_data = remove(input_data)
    
    img = Image.open(io.BytesIO(output_data))
    
    # Resize to 64x64
    print("Resizing...")
    img_resized = img.resize((64, 64), Image.Resampling.LANCZOS)
    
    img_resized.save(target_path, "PNG")
    print(f"Successfully replaced favicon at {target_path}")

except Exception as e:
    print(f"Error: {e}")
