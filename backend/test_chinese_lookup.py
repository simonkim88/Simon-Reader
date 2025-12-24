from backend.routers.dictionary import lookup_word, is_japanese
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

def test_lookup():
    word = "上衣"
    
    print(f"Testing word: {word}")
    
    # Case 1: Source = "zh"
    print("\n--- Testing source='zh' ---")
    result_zh = lookup_word(word, source="zh")
    pron_zh = result_zh.get("pronunciation", "None")
    print(f"Pronunciation: {pron_zh}")
    
    # Case 2: Source = "ja"
    print("\n--- Testing source='ja' ---")
    result_ja = lookup_word(word, source="ja")
    pron_ja = result_ja.get("pronunciation", "None")
    print(f"Pronunciation: {pron_ja}")

if __name__ == "__main__":
    test_lookup()
