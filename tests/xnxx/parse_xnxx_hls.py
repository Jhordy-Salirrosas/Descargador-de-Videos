import requests
import re

url = "https://www.xnxx.es/video-1bggft1c/dos_chicas_calientes_realmente_aman_el_sexo_anal"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

try:
    # Get page HTML
    r = requests.get(url, headers=headers, timeout=15)
    html = r.text
    
    # Find HLS URL
    hls_match = re.search(r'html5player\.setVideoHLS\(\'([^\']+)\'\)', html)
    if not hls_match:
        print("HLS URL not found in page")
        exit(1)
    
    hls_url = hls_match.group(1)
    print(f"Found HLS URL: {hls_url}\n")
    
    # Fetch HLS master playlist
    print("Fetching HLS master playlist...")
    hls_resp = requests.get(hls_url, headers=headers, timeout=15)
    hls_content = hls_resp.text
    
    print("\n=== HLS Master Playlist Content ===\n")
    print(hls_content)
    
    print("\n=== Parsing Available Qualities ===\n")
    
    # Parse m3u8 format
    # Look for #EXT-X-STREAM-INF lines which contain quality information
    qualities = []
    lines = hls_content.split('\n')
    
    for i, line in enumerate(lines):
        if line.startswith('#EXT-X-STREAM-INF:'):
            # Extract bandwidth and resolution
            bandwidth_match = re.search(r'BANDWIDTH=(\d+)', line)
            resolution_match = re.search(r'RESOLUTION=(\d+)x(\d+)', line)
            
            # Next line should be the playlist URL
            if i + 1 < len(lines):
                playlist_url = lines[i + 1].strip()
                
                if bandwidth_match and resolution_match:
                    width = int(resolution_match.group(1))
                    height = int(resolution_match.group(2))
                    bandwidth = int(bandwidth_match.group(1))
                    
                    # Construct full URL if relative
                    if not playlist_url.startswith('http'):
                        base_url = '/'.join(hls_url.split('/')[:-1])
                        playlist_url = f"{base_url}/{playlist_url}"
                    
                    qualities.append({
                        'resolution': f'{width}x{height}',
                        'height': height,
                        'width': width,
                        'bandwidth': bandwidth,
                        'url': playlist_url,
                        'label': f'{height}p'
                    })
    
    print(f"Found {len(qualities)} quality options:\n")
    for q in sorted(qualities, key=lambda x: x['height'], reverse=True):
        print(f"  • {q['label']} ({q['resolution']}) - Bandwidth: {q['bandwidth'] // 1000} Kbps")
        print(f"    URL: {q['url'][:80]}...")
        print()
        
except Exception as e:
    import traceback
    print(f"Error: {e}")
    print(traceback.format_exc())
