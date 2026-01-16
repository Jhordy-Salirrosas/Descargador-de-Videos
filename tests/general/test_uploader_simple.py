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
    
    with open('uploader_result.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("XNXX Uploader Extraction Test\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Title: {result.get('title', 'N/A')}\n")
        f.write(f"Uploader: {result.get('uploader', 'N/A')}\n")
        f.write(f"Total Formats: {len(result.get('formats', []))}\n\n")
        f.write("=" * 60 + "\n")
        
        if result.get('uploader') and result.get('uploader') != 'XNXX' and result.get('uploader') != 'Unknown':
            f.write("✓ SUCCESS: Uploader name extracted correctly!\n")
            f.write(f"✓ Video will be saved to folder: {result.get('uploader')}\n")
        else:
            f.write(f"✗ WARNING: Uploader is '{result.get('uploader')}'\n")
            f.write("  Expected a specific uploader name (e.g., 'keokistar')\n")
        
        f.write("=" * 60 + "\n")
    
    print(f"Uploader: {result.get('uploader')}")
    print("Result saved to uploader_result.txt")
    
except Exception as e:
    print(f"Error: {e}")
