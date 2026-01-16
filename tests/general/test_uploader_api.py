import requests
import json

url = "http://localhost:5000/analyze"
data = {
    "url": "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal",
    "browser": "brave"
}

try:
    response = requests.post(url, json=data, timeout=30)
    result = response.json()
    
    print("=" * 60)
    print("XNXX Uploader Extraction Test")
    print("=" * 60)
    print(f"\nTitle: {result.get('title', 'N/A')}")
    print(f"Uploader: {result.get('uploader', 'N/A')}")
    print(f"Total Formats: {len(result.get('formats', []))}")
    print("\n" + "=" * 60)
    
    if result.get('uploader') and result.get('uploader') != 'XNXX' and result.get('uploader') != 'Unknown':
        print("✓ SUCCESS: Uploader name extracted correctly!")
        print(f"✓ Video will be saved to folder: {result.get('uploader')}")
    else:
        print(f"✗ WARNING: Uploader is '{result.get('uploader')}'")
        print("  Expected a specific uploader name (e.g., 'keokistar')")
    
    print("=" * 60)
    
except Exception as e:
    print(f"Error: {e}")
