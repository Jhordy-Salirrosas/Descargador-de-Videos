import requests
import re
import json

url = "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    html = r.text
    
    print("=== Searching for XNXX Video URLs ===\n")
    
    # Search for all possible video-related JavaScript patterns
    patterns = [
        (r"html5player\.setVideoUrlHigh\('([^']+)'\)", "High Quality"),
        (r"html5player\.setVideoUrlLow\('([^']+)'\)", "Low Quality"),
        (r"html5player\.setVideoHLS\('([^']+)'\)", "HLS Stream"),
        (r"html5player\.setVideoUrl\('([^']+)'\)", "Standard URL"),
        (r'setVideoUrlHigh169\(\'([^\']+)\'\)', "High 16:9"),
        (r'setVideoUrlLow169\(\'([^\']+)\'\)', "Low 16:9"),
        (r'"url_high":"([^"]+)"', "JSON High"),
        (r'"url_low":"([^"]+)"', "JSON Low"),
        (r'"hls_url":"([^"]+)"', "JSON HLS"),
    ]
    
    for pattern, name in patterns:
        match = re.search(pattern, html)
        if match:
            print(f"✓ Found {name}:")
            print(f"  {match.group(1)[:80]}...")
            print()
        else:
            print(f"✗ NOT found: {name}")
    
    print("\n=== Looking for JSON video data ===\n")
    # Try to find JSON data embedded in script tags
    json_patterns = [
        r'xnxx\.video\.data\s*=\s*({[^;]+});',
        r'var\s+videoData\s*=\s*({[^;]+});',
        r'window\.__INITIAL_STATE__\s*=\s*({[^;]+});',
    ]
    
    for pattern in json_patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                print(f"✓ Found JSON data:")
                print(json.dumps(data, indent=2)[:500])
                print()
            except:
                print(f"✓ Found JSON-like data (couldn't parse):")
                print(match.group(1)[:200])
                print()
    
    print("\n=== Checking for m3u8/HLS URL ===\n")
    # HLS URLs typically end in .m3u8
    hls_matches = re.findall(r'https://[^"\'\s]+\.m3u8[^"\'\s]*', html)
    if hls_matches:
        print(f"✓ Found {len(hls_matches)} HLS URL(s):")
        for hls in hls_matches[:3]:
            print(f"  {hls}")
    else:
        print("✗ No HLS URLs found")
        
except Exception as e:
    print(f"Error: {e}")
