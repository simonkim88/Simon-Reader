import requests
import json

def check_examples(word):
    url = f"https://en.dict.naver.com/api3/enko/search?query={word}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://dict.naver.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        items = data.get('searchResultMap', {}).get('searchResultListMap', {}).get('WORD', {}).get('items', [])
        if items:
            item = items[0]
            print("Keys in item:", item.keys())
            # Check for potential example fields
            if 'meansCollector' in item:
                 print("MeansCollector found. Checking content...")
                 # meansCollector usually has meanings. Examples might be deeper or in a different field like 'example'
            
            # recursive search for "example" key
            def find_key(obj, target):
                if isinstance(obj, dict):
                    if target in obj: return True
                    for k, v in obj.items():
                        if find_key(v, target): return True
                elif isinstance(obj, list):
                    for item in obj:
                        if find_key(item, target): return True
                return False

            has_example = find_key(item, 'example')
            print(f"Has 'example' key in data: {has_example}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_examples("apple")
