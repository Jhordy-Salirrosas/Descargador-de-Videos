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
    
    print("=== Extracting Uploader from XNXX ===\n")
    
    uploader = None
    
    # Method 1: Try JSON uploader field
    uploader_match = re.search(r'"uploader"\s*:\s*"([^"]+)"', html)
    if uploader_match:
        uploader = uploader_match.group(1)
        print(f"✓ Found uploader from JSON: {uploader}")
    
    # Method 2: Try to find pornstar name from metadata
    if not uploader:
        # Look for pornstar in various formats
        pornstar_patterns = [
            r'<a[^>]*href="/pornstar/([^/"]+)"[^>]*>([^<]+)</a>',
            r'data-pornstar="([^"]+)"',
            r'class="[^"]*pornstar[^"]*"[^>]*>([^<]+)<',
        ]
        
        for pattern in pornstar_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                uploader = match.group(1) if match.lastindex == 1 else match.group(2)
                print(f"✓ Found pornstar from HTML: {uploader}")
                break
    
    # Method 3: Extract from tags if pornstar tag exists
    if not uploader:
        tags_match = re.search(r'"video_tags"\s*:\s*\[([^\]]+)\]', html)
        if tags_match:
            tags_str = tags_match.group(1)
            print(f"Tags found: {tags_str[:200]}...")
            # Tags are usually generic, not useful for uploader
    
    # Fallback
    if not uploader:
        uploader = "Unknown"
        print(f"✗ No uploader found, using: {uploader}")
    
    print(f"\n=== Final Result ===")
    print(f"Uploader: {uploader}")
    
    # Test sanitization
    sanitized = "".join([c for c in uploader if c.isalnum() or c in (' ', '-', '_')]).strip()
    if not sanitized:
        sanitized = 'Unknown'
    
    print(f"Sanitized (for folder name): {sanitized}")
    
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
