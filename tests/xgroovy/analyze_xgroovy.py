import requests
import re
import json
import sys

# Use command line argument or default
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    # Default test URL - user will provide a real one
    print("Usage: py analyze_xgroovy.py <URL>")
    print("\nUsing generic xgroovy domain for pattern detection...")
    url = "https://es.xgroovy.com/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    print(f"\n=== Analyzing xgroovy.com ===")
    print(f"URL: {url}\n")
    
    r = requests.get(url, headers=headers, timeout=15)
    html = r.text
    
    print(f"HTML Length: {len(html)} bytes\n")
    
    # Save HTML for inspection
    with open('xgroovy_source.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Saved HTML to xgroovy_source.html\n")
    
    print("=== Searching for Video Metadata ===\n")
    
    # Search for uploader/pornstar
    print("1. Uploader/Pornstar Patterns:")
    uploader_patterns = [
        (r'"uploader"\s*:\s*"([^"]+)"', "JSON uploader"),
        (r'"author"\s*:\s*"([^"]+)"', "JSON author"),  
        (r'"channel"\s*:\s*"([^"]+)"', "JSON channel"),
        (r'<a[^>]*href="/pornstar/([^/"]+)"', "Pornstar link"),
        (r'<a[^>]*href="/models?/([^/"]+)"', "Model link"),
        (r'<a[^>]*href="/channels?/([^/"]+)"', "Channel link"),
        (r'data-model="([^"]+)"', "Data model"),
        (r'class="model-name"[^>]*>([^<]+)<', "Model name class"),
    ]
    
    uploader_found = None
    for pattern, name in uploader_patterns:
        match = re.search(pattern, html, re.IGNORECASE)
        if match:
            print(f"  ✓ {name}: {match.group(1)}")
            if not uploader_found:
                uploader_found = match.group(1)
        else:
            print(f"  ✗ {name}: Not found")
    
    if uploader_found:
        print(f"\n  ✓ RECOMMENDED UPLOADER: {uploader_found}")
    else:
        print("\n  ⚠ WARNING: No uploader pattern found!")
    
    # Search for video URLs
    print("\n2. Video URL Patterns:")
    video_patterns = [
        (r'\.m3u8[^"\'\s]*', "HLS/m3u8"),
        (r'setVideoHLS\([\'"]([^\'"]+)[\'"]', "setVideoHLS"),
        (r'setVideoUrl\([\'"]([^\'"]+)[\'"]', "setVideoUrl"),
        (r'"videoUrl"\s*:\s*"([^"]+)"', "JSON videoUrl"),
        (r'"video_url"\s*:\s*"([^"]+)"', "JSON video_url"),
    ]
    
    for pattern, name in video_patterns:
        matches = re.findall(pattern, html)
        if matches:
            print(f"  ✓ {name}: Found {len(matches)} match(es)")
            for match in matches[:2]:  # Show first 2
                print(f"    - {match[:80]}...")
        else:
            print(f"  ✗ {name}: Not found")
    
    # Check if yt-dlp has a specific extractor
    if url != "https://es.xgroovy.com/":
        print("\n3. Testing with yt-dlp:")
        import subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'yt_dlp', '--dump-json', '--no-warnings', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            try:
                info = json.loads(result.stdout)
                print(f"  ✓ yt-dlp extraction successful!")
                print(f"  - Extractor: {info.get('extractor', 'N/A')}")
                print(f"  - Title: {info.get('title', 'N/A')}")
                print(f"  - Uploader: {info.get('uploader', 'N/A')}")
                print(f"  - Formats: {len(info.get('formats', []))}")
            except:
                print(f"  ⚠ Could not parse yt-dlp output")
        else:
            print(f"  ✗ yt-dlp failed to extract")
            print(f"  Error: {result.stderr[:200]}")
    else:
        print("\n3. Provide a specific video URL to test with yt-dlp")
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
