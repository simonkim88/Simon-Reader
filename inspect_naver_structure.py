import requests
import json

def inspect_structure(word):
    url = f"https://en.dict.naver.com/api3/enko/search?query={word}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://dict.naver.com/'
    }
    
    response = requests.get(url, headers=headers, timeout=5)
    data = response.json()
    
    # Traverse and match keys
    def traverse(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_path = f"{path}.{k}" if path else k
                if "example" in k.lower():
                    print(f"Found key '{k}' at {new_path}")
                    if isinstance(v, str):
                        print(f"  Value: {v[:50]}...")
                    elif isinstance(v, list):
                         print(f"  Value (List len): {len(v)}")
                         if len(v) > 0 and isinstance(v[0], dict):
                             print(f"  First item keys: {v[0].keys()}")
                
                traverse(v, new_path)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                traverse(item, f"{path}[{i}]")

    print(f"--- Inspecting structure for '{word}' ---")
    traverse(data)

if __name__ == "__main__":
    inspect_structure("apple")
