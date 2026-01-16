import yt_dlp
import json

url = "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal"

print(f"Testing URL: {url}")

ydl_opts = {
    'quiet': True,
    'dump_json': True,
    'no_warnings': True,
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print("Title:", info.get('title'))
        print("Formats found:", len(info.get('formats', [])))
        
        for f in info.get('formats', []):
            print(f"ID: {f.get('format_id')}")
            print(f"Ext: {f.get('ext')}")
            print(f"Resolution: {f.get('resolution')}")
            print(f"Height: {f.get('height')}")
            print(f"Note: {f.get('format_note')}")
            print(f"URL: {f.get('url')}")
            print("-" * 20)
            
except Exception as e:
    print(f"Error: {e}")
