import requests
import re
import json

url = "https://es.xgroovy.com/videos/370148/enjoy-hot-joi-from-sexy-slim-busty-beauty-sia-siberia-and-cum-with-her/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

print("=== Detailed xgroovy.com Analysis ===\n")

try:
    # Get HTML
    r = requests.get(url, headers=headers, timeout=15)
    html = r.text
    
    print(f"HTML Length: {len(html)} bytes\n")
    
    # Look for JSON-LD structured data
    print("1. Searching for JSON-LD Structured Data:")
    jsonld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
    jsonld_matches = re.findall(jsonld_pattern, html, re.DOTALL)
    
    if jsonld_matches:
        print(f"  Found {len(jsonld_matches)} JSON-LD block(s)\n")
        for i, jsonld_text in enumerate(jsonld_matches, 1):
            try:
                data = json.loads(jsonld_text.strip())
                print(f"  Block {i}:")
                print(f"    Type: {data.get('@type', 'Unknown')}")
                if 'author' in data:
                    print(f"    Author: {data.get('author')}")
                if 'creator' in data:
                    print(f"    Creator: {data.get('creator')}")
                if 'actor' in data:
                    print(f"    Actor: {data.get('actor')}")
                if 'uploader' in data:
                    print(f"    Uploader: {data.get('uploader')}")
                print()
            except Exception as e:
                print(f"  Block {i}: Could not parse - {e}\n")
    else:
        print("  No JSON-LD found\n")
    
    # Look for video metadata in script tags
    print("2. Searching for Video Metadata in Scripts:")
    
    # Common patterns for video sites
    meta_patterns = [
        (r'video_title["\']?\s*:[\s"\']*([^"\']+)', "video_title"),
        (r'pornstar["\']?\s*:[\s"\']*([^"\']+)', "pornstar"),
        (r'model["\']?\s*:[\s"\']*([^"\']+)', "model"),
        (r'uploader["\']?\s*:[\s"\']*([^"\']+)', "uploader"),
        (r'channel["\']?\s*:[\s"\']*([^"\']+)', "channel"),
    ]
    
    for pattern, name in meta_patterns:
        matches = re.findall(pattern, html, re.IGNORECASE)
        if matches:
            print(f"  ✓ {name}: {matches[0]}")
        else:
            print(f"  ✗ {name}: Not found")
    
    print("\n3. Test with yt-dlp extractor:")
    import subprocess
    import sys
    
    result = subprocess.run(
        [sys.executable, '-m', 'yt_dlp', '--dump-json', '--no-warnings', url],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        info = json.loads(result.stdout)
        print(f"  Extractor: {info.get('extractor')}")
        print(f"  Extractor Key: {info.get('extractor_key')}")
        print(f"  Title: {info.get('title', 'N/A')[:60]}...")
        print(f"  Uploader: {info.get('uploader', 'N/A')}")
        print(f"  Channel: {info.get('channel', 'N/A')}")
        print(f"  Creator: {info.get('creator', 'N/A')}")
        
        # Check all available metadata keys
        print(f"\n  Available metadata keys:")
        keys = list(info.keys())
        print(f"  {', '.join(keys[:15])}...")
        
        # Save full JSON
        with open('xgroovy_ytdlp_info.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        print(f"\n  ✓ Full metadata saved to xgroovy_ytdlp_info.json")
    else:
        print(f"  ✗ yt-dlp failed")
        print(f"  {result.stderr[:200]}")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
