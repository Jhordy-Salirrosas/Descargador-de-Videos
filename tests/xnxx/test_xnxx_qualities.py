import requests
import json

url = "http://localhost:5000/analyze"
data = {
    "url": "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal",
    "browser": "brave"
}

print("Testing XNXX Quality Extraction...")
print("=" * 60)

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status Code: {response.status_code}\n")
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Uploader: {result.get('uploader', 'N/A')}")
        print(f"Type: {result.get('type', 'N/A')}")
        print(f"Total Formats: {len(result.get('formats', []))}\n")
        
        if 'formats' in result and result['formats']:
            print("=" * 60)
            print("AVAILABLE QUALITIES:")
            print("=" * 60)
            
            for i, fmt in enumerate(result['formats'], 1):
                print(f"\n{i}. Resolution: {fmt.get('resolution')}")
                print(f"   Height: {fmt.get('height')}p")
                print(f"   Width: {fmt.get('width', 'N/A')}")
                print(f"   Extension: {fmt.get('ext')}")
                print(f"   Note: {fmt.get('note')}")
                print(f"   Size: {fmt.get('size')}")
                
            print("\n" + "=" * 60)
            print(f"✓ SUCCESS: Found {len(result['formats'])} quality options!")
            print("=" * 60)
        else:
            print("✗ ERROR: No formats found in response")
            print("\nFull Response:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"✗ ERROR: Got status code {response.status_code}")
        print(f"Response: {response.text}")
            
except Exception as e:
    print(f"✗ EXCEPTION: {e}")
    import traceback
    print(traceback.format_exc())
