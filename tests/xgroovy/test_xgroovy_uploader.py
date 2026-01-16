import requests
import json

url = "http://localhost:5000/analyze"
data = {
    "url": "https://es.xgroovy.com/videos/370148/enjoy-hot-joi-from-sexy-slim-busty-beauty-sia-siberia-and-cum-with-her/",
    "browser": "brave"
}

try:
    response = requests.post(url, json=data, timeout=40)
    result = response.json()
    
    print("=" * 80)
    print("XGROOVY UPLOADER EXTRACTION TEST")
    print("=" * 80)
    print(f"\nTitle: {result.get('title', 'N/A')}")
    print(f"Uploader: {result.get('uploader', 'N/A')}")
    print(f"Total Formats: {len(result.get('formats', []))}")
    
    print("\n" + "=" * 80)
    
    expected_names = ['sia siberia', 'sia', 'siberia']
    uploader_lower = result.get('uploader', '').lower()
    
    if any(name in uploader_lower for name in expected_names):
        print("✓ SUCCESS: Uploader extracted correctly from title!")
        print(f"✓ Video will be saved to folder: '{result.get('uploader')}'")
        print(f"\n  Before: Unknown/")
        print(f"  After:  {result.get('uploader')}/")
    else:
        print(f"✗ FAILED: Uploader is '{result.get('uploader')}'")
        print("  Expected something containing 'Sia Siberia'")
    
    print("=" * 80)
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
