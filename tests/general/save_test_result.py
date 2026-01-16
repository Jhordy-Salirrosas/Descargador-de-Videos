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
    
    with open('xnxx_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"Total formats found: {len(result.get('formats', []))}")
    for fmt in result.get('formats', []):
        print(f"- {fmt.get('resolution')} ({fmt.get('height')}p) - {fmt.get('note')}")
    
except Exception as e:
    print(f"Error: {e}")
