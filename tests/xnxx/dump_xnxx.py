import requests
url = "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
}
try:
    r = requests.get(url, headers=headers)
    with open('xnxx_source.html', 'w', encoding='utf-8') as f:
        f.write(r.text)
    print("Saved xnxx_source.html")
except Exception as e:
    print(f"Error: {e}")
