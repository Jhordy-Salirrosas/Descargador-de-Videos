import requests
import json

url = "http://localhost:5000/analyze"
data = {
    "url": "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal",
    "browser": "brave"
}

try:
    response = requests.post(url, json=data, timeout=30)
    print(f"Status Code: {response.status_code}")
    print("\nResponse JSON:")
    result = response.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if 'formats' in result:
        print(f"\n\n=== FOUND {len(result['formats'])} QUALITIES ===\n")
        for fmt in result['formats']:
            print(f"  • {fmt.get('resolution')} - {fmt.get('note')} - Height: {fmt.get('height')}p")
            
except Exception as e:
    print(f"Error: {e}")
