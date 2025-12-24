import sys
import os

# Add backend directory to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from naver_scraper import scrape_naver_dict

if __name__ == "__main__":
    print("Testing 'apple'...")
    result = scrape_naver_dict("apple")
    if result and "examples" in result:
        print(f"Examples found: {len(result['examples'])}")
        print("Examples:", result['examples'])
    else:
        print("No examples found for apple")

    print("\nTesting 'run'...")
    result = scrape_naver_dict("run")
    if result and "examples" in result:
        print(f"Examples found: {len(result['examples'])}")
        print("Examples:", result['examples'])
    else:
        print("No examples found for run")
