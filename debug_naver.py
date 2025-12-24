import requests
import json

def inspect_naver(word, lang="en"):
    url = f"https://en.dict.naver.com/api3/enko/search?query={word}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://dict.naver.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        # Save to file for inspection
        with open('naver_api_dump.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print("Dumped to naver_api_dump.json")
        
        # Print some structure hints
        if 'searchResultMap' in data:
            print("Keys in searchResultMap:", data['searchResultMap'].keys())
            if 'searchResultListMap' in data['searchResultMap']:
                print("Keys in searchResultListMap:", data['searchResultMap']['searchResultListMap'].keys())
                word_data = data['searchResultMap']['searchResultListMap'].get('WORD')
                if word_data:
                    print("Keys in WORD:", word_data.keys())
                    if 'items' in word_data:
                        print("Number of items:", len(word_data['items']))
                        if len(word_data['items']) > 0:
                            item = word_data['items'][0]
                            print("Keys in first item:", item.keys())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_naver("apple")
