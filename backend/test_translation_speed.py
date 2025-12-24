import time
from deep_translator import GoogleTranslator

def test_speed():
    text = "This is a sentence to test the translation speed."
    
    print("--- First Call (Init + Translate) ---")
    start = time.time()
    translator = GoogleTranslator(source='auto', target='ko')
    res = translator.translate(text)
    end = time.time()
    print(f"Result: {res}")
    print(f"Time: {end - start:.4f}s")
    
    print("\n--- Second Call (New Instance) ---")
    start = time.time()
    translator = GoogleTranslator(source='auto', target='ko')
    res = translator.translate(text)
    end = time.time()
    print(f"Time: {end - start:.4f}s")

    print("\n--- Third Call (Reused Instance) ---")
    start = time.time()
    res = translator.translate(text)
    end = time.time()
    print(f"Time: {end - start:.4f}s")

if __name__ == "__main__":
    test_speed()
