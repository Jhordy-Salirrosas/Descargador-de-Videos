import yt_dlp
import requests
import re

url = "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal"

print(f"--- 1. Testing yt-dlp with standard user-agent ---")
ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(f"Formats found (with UA): {len(info.get('formats', []))}")
except Exception as e:
    print(f"yt-dlp error: {e}")

print(f"\n--- 2. Manual HTML Inspection ---")
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://www.xnxx.es'
}
try:
    r = requests.get(url, headers=headers)
    html = r.text
    print(f"HTML Length: {len(html)}")
    
    # Check for common XNXX patterns
    search_high = re.search(r"setVideoUrlHigh\('([^']+)'\)", html)
    search_low = re.search(r"setVideoUrlLow\('([^']+)'\)", html)
    search_hls = re.search(r"setVideoHLS\('([^']+)'\)", html)
    
    if search_high: print(f"Found High URL: {search_high.group(1)[:50]}...")
    else: print("High URL NOT found")
    
    if search_low: print(f"Found Low URL: {search_low.group(1)[:50]}...")
    else: print("Low URL NOT found")
    
    if search_hls: print(f"Found HLS URL: {search_hls.group(1)[:50]}...")
    else: print("HLS URL NOT found")

except Exception as e:
    print(f"Requests error: {e}")
