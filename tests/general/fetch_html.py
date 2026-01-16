import requests

url = "https://www.pornoxo.com/videos/2620994/sia-siberia-masturbation-with-dp-in-the-car/?utm_source=awn&utm_medium=tgp&utm_campaign=cpc"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.pornoxo.com/'
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Page source saved to page_source.html")
except Exception as e:
    print(f"Error: {e}")
