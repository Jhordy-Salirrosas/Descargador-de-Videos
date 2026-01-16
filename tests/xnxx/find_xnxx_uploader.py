import requests
import re
import json

# Test with the URL from the screenshot (Sia Siberia)
url = "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    r = requests.get(url, headers=headers, timeout=15)
    html = r.text
    
    print("=== Searching for Uploader/Actress Name ===\n")
    
    # Common patterns for uploader/pornstar name in adult sites
    patterns = [
        (r'<meta name="author" content="([^"]+)"', "Meta Author"),
        (r'property="video:actor" content="([^"]+)"', "Video Actor"),
        (r'class="metadata-pornstar.*?href="[^"]*">([^<]+)<', "Pornstar Link"),
        (r'"uploader":"([^"]+)"', "JSON Uploader"),
        (r'"models":\s*\[([^\]]+)\]', "JSON Models"),
        (r'<a[^>]*class="[^"]*is-pornstar[^"]*"[^>]*>([^<]+)<', "Pornstar Class"),
        (r'data-pornstar="([^"]+)"', "Data Pornstar"),
        (r'<span class="name">([^<]+)</span>', "Span Name"),
        (r'/pornstar/([^/"]+)', "Pornstar URL"),
    ]
    
    print("Trying different patterns:\n")
    for pattern, name in patterns:
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        if matches:
            print(f"✓ {name}:")
            for match in matches[:5]:  # Show first 5 matches
                print(f"  - {match.strip()}")
            print()
        else:
            print(f"✗ {name}: Not found")
    
    # Look for JSON-LD structured data
    print("\n=== Searching for JSON-LD Structured Data ===\n")
    jsonld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
    jsonld_matches = re.findall(jsonld_pattern, html, re.DOTALL)
    
    if jsonld_matches:
        print(f"Found {len(jsonld_matches)} JSON-LD blocks\n")
        for i, jsonld in enumerate(jsonld_matches, 1):
            try:
                data = json.loads(jsonld.strip())
                print(f"Block {i}:")
                if 'author' in data:
                    print(f"  Author: {data['author']}")
                if 'creator' in data:
                    print(f"  Creator: {data['creator']}")
                if 'actor' in data:
                    print(f"  Actor: {data['actor']}")
                print()
            except:
                print(f"Block {i}: Could not parse JSON")
    else:
        print("No JSON-LD blocks found")
        
    # Search for common adult site metadata
    print("\n=== Looking for Common Metadata Tags ===\n")
    
    # Search in first 50000 chars for efficiency
    search_text = html[:50000]
    
    if 'pornstar' in search_text.lower():
        print("✓ Found 'pornstar' mention in HTML")
        # Extract context around pornstar
        import re
        for match in re.finditer(r'.{0,100}pornstar.{0,100}', search_text, re.IGNORECASE):
            snippet = match.group(0).replace('\n', ' ').replace('\r', '')
            print(f"  Context: ...{snippet}...")
            
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
