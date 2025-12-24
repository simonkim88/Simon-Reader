import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()

def scrape_naver_dict(word, lang="en"):
    """
    Scrape Naver Dictionary for a word using internal APIs.
    lang: 'en' for English-Korean, 'ja' for Japanese-Korean
    """
    
    if lang == "ja":
        # Japanese-Korean API
        url = f"https://ja.dict.naver.com/api3/jako/search?query={word}"
    elif lang == "zh":
        # Chinese-Korean API
        url = f"https://zh.dict.naver.com/api3/zhko/search?query={word}"
    else:
        # English-Korean API
        url = f"https://en.dict.naver.com/api3/enko/search?query={word}"
        
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://dict.naver.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        definitions = []
        examples = []
        
        # Navigate JSON structure: searchResultMap -> searchResultListMap -> WORD -> items
        if 'searchResultMap' in data and 'searchResultListMap' in data['searchResultMap']:
            res_map = data['searchResultMap']['searchResultListMap']
            if 'WORD' in res_map:
                items = res_map['WORD']['items']
                if items:
                    # Get first item (best match)
                    item = items[0]
                    
                    # Extract pronunciation
                    pronunciation = None
                    if lang == "ja":
                        pronunciation = item.get('expMeaningRead')
                        if not pronunciation:
                             # Fallback to expEntry (often contains the reading/Kana)
                             pronunciation = item.get('expEntry')
                        if not pronunciation:
                             # Fallback to expAudioRead
                             pronunciation = item.get('expAudioRead')
                    elif lang == "zh":
                        # Chinese Pinyin is usually in searchPhoneticSymbolList
                        phonetic_list = item.get('searchPhoneticSymbolList', [])
                        if phonetic_list and len(phonetic_list) > 0:
                            pronunciation = phonetic_list[0].get('symbolValue')
                        
                        # Fallback to expEntry if it looks like Pinyin (unlikely but safe)
                        if not pronunciation:
                             pronunciation = item.get('expEntry')

                    # Clean up pronunciation (sometimes it has HTML or extra chars)
                    if pronunciation:
                        pronunciation = re.sub(r'<[^>]+>', '', pronunciation).strip()
                    
                    # Extract meanings from meansCollector
                    if 'meansCollector' in item:
                        for collector in item['meansCollector']:
                            for mean in collector.get('means', []):
                                if 'value' in mean:
                                    # Remove HTML tags if any (sometimes they exist)
                                    clean_def = re.sub(r'<[^>]+>', '', mean['value'])
                                    definitions.append(clean_def)
                            if len(definitions) >= 6: # Limit to 6 definitions
                                break
                                
                    if definitions:
                        # Extract Examples from 'EXAMPLE' section
                        if 'EXAMPLE' in res_map:
                            ex_items = res_map['EXAMPLE']['items']
                            for ex_item in ex_items[:2]: # Limit to 2 examples
                                if 'expExample1' in ex_item and 'expExample2' in ex_item:
                                    # Clean up HTML tags
                                    en = re.sub(r'<[^>]+>', '', ex_item['expExample1']).strip()
                                    ko = re.sub(r'<[^>]+>', '', ex_item['expExample2']).strip()
                                    if en and ko:
                                        examples.append(f"{en} ({ko})")
                        
                        # Fallback to 'VLIVE' if no examples found
                        if not examples and 'VLIVE' in res_map:
                             ex_items = res_map['VLIVE']['items']
                             for ex_item in ex_items[:2]:
                                if 'expExample1' in ex_item and 'expExample2' in ex_item:
                                    en = re.sub(r'<[^>]+>', '', ex_item['expExample1']).strip()
                                    ko = re.sub(r'<[^>]+>', '', ex_item['expExample2']).strip()
                                    if en and ko:
                                        examples.append(f"{en} ({ko})")

                        return {
                            "definition": "; ".join(definitions),
                            "pronunciation": pronunciation,
                            "examples": examples
                        }
            
        return None

    except Exception as e:
        print(f"Error scraping Naver Dict: {e}")
        return None
