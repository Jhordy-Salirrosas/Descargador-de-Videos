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
    
    # Save result to file
    with open('xgroovy_test_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    uploader = result.get('uploader', 'N/A')
    print(f"Uploader: {uploader}")
    print("Full result saved to xgroovy_test_result.json")
    
except Exception as e:
    print(f"Error: {e}")
