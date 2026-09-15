import os
import logging
import threading
import uuid
import datetime
import re
import shutil
import json
import time
import sys
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import requests
from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import yt_dlp
from yt_dlp.networking.impersonate import ImpersonateTarget


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- PATCH: Add likely FFmpeg paths for Windows (Winget/Manual) ---
possible_ffmpeg_paths = [
    os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Links'),
    r"C:\Program Files\ffmpeg\bin",
    r"C:\ffmpeg\bin"
]
for path in possible_ffmpeg_paths:
    if os.path.isdir(path) and path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + path
        logger.info(f"Added to PATH: {path}")

def detect_ffmpeg_location():
    """Return FFmpeg bin directory if available, otherwise None."""
    ffmpeg_exe = shutil.which('ffmpeg')
    if ffmpeg_exe:
        return os.path.dirname(ffmpeg_exe)

    candidates = [
        os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\WinGet\Links\ffmpeg.exe'),
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return os.path.dirname(candidate)

    # Portable fallback: use bundled binary from imageio-ffmpeg if installed.
    try:
        import imageio_ffmpeg
        bundled_exe = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled_exe and os.path.exists(bundled_exe):
            return os.path.dirname(bundled_exe)
    except Exception:
        pass

    return None

FFMPEG_LOCATION = detect_ffmpeg_location()
if FFMPEG_LOCATION:
    logger.info(f"Using FFmpeg from: {FFMPEG_LOCATION}")
else:
    logger.warning("FFmpeg not detected. Some formats may fail to post-process.")
# ------------------------------------------------------------------

app = Flask(__name__)

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, 'data', 'history.json')
CONFIG_FILE = os.path.join(BASE_DIR, 'data', 'config.json')
PERSISTENT_COOKIES_FILE = os.path.join(BASE_DIR, 'data', 'cookies.txt')

import base64

# --- CLOUD PERSISTENCE AUTOLOAD ---
# Render's free tier deletes runtime files on restart. To automate this permanently:
if os.environ.get('YT_COOKIES_CONTENT'):
    try:
        os.makedirs(os.path.dirname(PERSISTENT_COOKIES_FILE), exist_ok=True)
        env_cookies = os.environ.get('YT_COOKIES_CONTENT').strip()
        
        # Check if the content is base64 encoded (starts with standard base64 for "# Netscape" -> "IyBOZXRz")
        # Or if it doesn't contain spaces and has valid base64 characters
        try:
            # Try to decode it as base64 first
            decoded_bytes = base64.b64decode(env_cookies)
            decoded_str = decoded_bytes.decode('utf-8')
            if "# Netscape HTTP Cookie File" in decoded_str or ".com\t" in decoded_str:
                env_cookies = decoded_str
                logger.info("Base64 cookie format detected and decoded.")
            else:
                # If it decoded but doesn't look like cookies, revert to original
                env_cookies = env_cookies.replace('\\n', '\n')
        except Exception:
            # Not valid base64, use as raw text
            env_cookies = env_cookies.replace('\\n', '\n')

        with open(PERSISTENT_COOKIES_FILE, 'w', encoding='utf-8') as f:
            f.write(env_cookies)
        logger.info("Cookies automáticos cargados desde Variable de Entorno 'YT_COOKIES_CONTENT'.")
    except Exception as e:
        logger.error(f"Error cargando cookies desde variable de entorno: {e}")
DEFAULT_MAX_CONCURRENT_DOWNLOADS = 2

# Load Config
config = {}
TEMP_DOWNLOADS_DIR = os.path.join(BASE_DIR, 'temp_downloads') # Default
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if config.get('download_path'):
                TEMP_DOWNLOADS_DIR = config['download_path']
    except Exception as e:
        logger.error(f"Error loading config: {e}")

MAX_CONCURRENT_DOWNLOADS = int(
    os.environ.get(
        'MAX_CONCURRENT_DOWNLOADS',
        str(config.get('max_concurrent_downloads', DEFAULT_MAX_CONCURRENT_DOWNLOADS))
    )
)
if MAX_CONCURRENT_DOWNLOADS < 1:
    MAX_CONCURRENT_DOWNLOADS = DEFAULT_MAX_CONCURRENT_DOWNLOADS

# Ensure directory exists
os.makedirs(TEMP_DOWNLOADS_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
download_progress = {}
abort_signals = {}
download_futures = {}
history_lock = threading.RLock()
download_state_lock = threading.RLock()
download_executor = ThreadPoolExecutor(
    max_workers=MAX_CONCURRENT_DOWNLOADS,
    thread_name_prefix='download-worker'
)

# Ensure temp dirs exist
os.makedirs(TEMP_DOWNLOADS_DIR, exist_ok=True)

def get_cookies_path(session_id):
    cookies_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', 'cookies')
    os.makedirs(cookies_dir, exist_ok=True)
    return os.path.join(cookies_dir, f"temp_cookies_{session_id}.txt")

def _load_history_unlocked():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def _write_history_unlocked(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def set_download_progress(download_id, patch):
    with download_state_lock:
        current = download_progress.get(download_id, {})
        current.update(patch)
        download_progress[download_id] = current

def get_queue_stats():
    with download_state_lock:
        active = 0
        queued = 0
        finished_ids = []
        for download_id, future in download_futures.items():
            if future.running():
                active += 1
            elif future.done():
                finished_ids.append(download_id)
            else:
                queued += 1

        for download_id in finished_ids:
            download_futures.pop(download_id, None)

        return {
            'max_workers': MAX_CONCURRENT_DOWNLOADS,
            'active': active,
            'queued': queued,
            'tracked': len(download_futures),
        }

def _is_within_path(path_value, base_path):
    try:
        return os.path.commonpath([os.path.abspath(path_value), os.path.abspath(base_path)]) == os.path.abspath(base_path)
    except Exception:
        return False

def load_history():
    with history_lock:
        return _load_history_unlocked()

def save_history_entry(entry):
    with history_lock:
        history = _load_history_unlocked()
        existing_index = next(
            (i for i, item in enumerate(history) if item.get('download_id') == entry.get('download_id')),
            None
        )
        if existing_index is None:
            history.insert(0, entry)
        else:
            history[existing_index].update(entry)

        try:
            _write_history_unlocked(history)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

def update_history_status(download_id, status, file_path=None):
    with history_lock:
        history = _load_history_unlocked()
        updated = False
        for item in history:
            if item.get('download_id') == download_id:
                item['status'] = status
                if file_path:
                    item['file_path'] = file_path
                updated = True
                break
        if updated:
            try:
                _write_history_unlocked(history)
            except Exception:
                pass

def normalize_uploader_name(uploader):
    """
    Normaliza el nombre del uploader para evitar carpetas duplicadas.
    - Reemplaza guiones bajos con espacios
    - Capitaliza cada palabra
    - Elimina caracteres especiales excepto espacios y guiones
    - Retorna 'Unknown' si el nombre estÃ¡ vacÃ­o
    """
    if not uploader or uploader == 'Unknown':
        return 'Unknown'
    
    # Reemplazar guiones bajos con espacios
    name = uploader.replace('_', ' ')
    
    # Eliminar caracteres especiales, mantener solo alfanumÃ©ricos, espacios y guiones
    name = "".join([c for c in name if c.isalnum() or c in (' ', '-')]).strip()
    
    # Capitalizar cada palabra (Title Case)
    name = ' '.join(word.capitalize() for word in name.split())
    
    # Si despuÃ©s de limpiar estÃ¡ vacÃ­o, retornar Unknown
    if not name:
        return 'Unknown'
    
    return name

def get_site_name(url):
    """
    Extrae el nombre del sitio desde la URL para usar como fallback
    cuando el uploader es Unknown
    """
    if not url:
        return 'Unknown Site'
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '').replace('es.', '')
        
        # Mapeo de sitios conocidos
        site_map = {
            'xnxx.com': 'XNXX',
            'xvideos.com': 'XVideos',
            'pornhub.com': 'Pornhub',
            'xgroovy.com': 'XGroovy',
            'youporn.com': 'YouPorn',
            'redtube.com': 'RedTube',
            'tube8.com': 'Tube8',
            'pornoxo.com': 'PornoXO',
        }
        
        for site_domain, site_name in site_map.items():
            if site_domain in domain:
                return site_name
        
        # Si no estÃ¡ en el mapa, usar dominio principal capitalizado
        parts = domain.split('.')
        if len(parts) >= 2:
            return parts[-2].capitalize()
        
        return 'Unknown Site'
    except Exception:
        return 'Unknown Site'

def format_bytes(size):
    if not size: return "0 B"
    power = 2**10
    n = size
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    count = 0
    while n > power:
        n /= power
        count += 1
    return f"{n:.2f} {power_labels[count]}B"

def sanitize_ytdlp_error(raw_error, source_url=None):
    """Extract a concise human-readable error from verbose yt-dlp stderr."""
    if not raw_error:
        return "No se pudo analizar el enlace (error desconocido)."

    clean = re.sub(r'\x1b\[[0-9;]*m', '', raw_error)
    lines = [line.strip() for line in clean.splitlines() if line.strip()]

    # Prefer explicit ERROR line from yt-dlp.
    error_line = next((line for line in lines if line.startswith('ERROR:')), None)
    if not error_line:
        # Fallback to first non-debug line.
        error_line = next((line for line in lines if not line.startswith('[debug]')), lines[0])

    readable = error_line.replace('ERROR:', '').strip()

    if 'HTTP Error 410' in readable or '410' in readable:
        return 'Este video fue eliminado del sitio y ya no estÃ¡ disponible (HTTP 410 Gone). No es posible descargarlo.'
    if 'HTTP Error 404' in readable or '404' in readable:
        source = (source_url or '').lower()
        if 'hqporner.com' in source:
            return 'HQPorner suele requerir URL canÃ³nica. Intenta con el mismo enlace terminando en .html o con formato /hdporn/<id>. Si persiste, el video puede estar no disponible en tu regiÃ³n/red.'
        return 'La URL no existe o ya no estÃ¡ disponible (HTTP 404). Verifica el enlace.'
    if 'Sign in' in readable or 'login' in readable.lower():
        return 'El sitio requiere autenticaciÃ³n. Intenta con cookies vÃ¡lidas del navegador.'
    if 'Unsupported URL' in readable:
        source = (source_url or '').lower()
        if 'hqporner.com' in readable.lower() or 'hqporner.com' in source:
            return 'HQPorner carga este video mediante un proveedor embebido no compatible o bloqueado en esta red. Prueba con otra red/VPN o usa otro enlace del sitio.'
        return 'El enlace no es compatible con los extractores actuales.'
    if 'Unable to download webpage' in readable:
        return f'No se pudo descargar la pÃ¡gina del video. Detalle: {readable}'

    return readable

def progress_hook(d):
    download_id = d.get('info_dict', {}).get('_download_id')
    if not download_id:
        return

    # Extract detailed stats
    status = d.get('status')
    
    if status == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)
        percent_str = d.get('_percent_str', '0%')
        # Remove ANSI codes if present (yt-dlp sometimes adds colors)
        percent_str = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
        
        speed_str = d.get('_speed_str', 'N/A')
        speed_str = re.sub(r'\x1b\[[0-9;]*m', '', speed_str)
        
        # Calculate nice strings
        downloaded_str = format_bytes(downloaded)
        total_str = format_bytes(total_bytes)
        
        # Determine remaining
        remaining_str = "Unknown"
        if total_bytes > downloaded:
            remaining_str = format_bytes(total_bytes - downloaded)
        
        set_download_progress(download_id, {
            'status': 'downloading',
            'percent': percent_str,
            'speed': speed_str,
            'downloaded': downloaded_str,
            'total': total_str,
            'remaining': remaining_str,
            'filename': d.get('filename', 'Downloading...')
        })
        
    elif status == 'finished':
        # This means the *download* part is done, but FFmpeg might merge now.
        set_download_progress(download_id, {
            'status': 'processing',
            'percent': '100%',
            'speed': 'Processing...',
            'filename': d.get('filename')
        })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history', methods=['GET'])
def get_history_route():
    """Retorna historial completo con estado de existencia de archivos"""
    history = load_history()
    
    # Agregar campo file_exists a cada entrada
    for entry in history:
        file_path = entry.get('file_path', '')
        entry['file_exists'] = bool(file_path and os.path.exists(file_path))
        
        # Agregar tamaÃ±o de archivo si existe
        if entry['file_exists']:
            try:
                entry['file_size'] = os.path.getsize(file_path)
            except Exception:
                entry['file_size'] = 0
    
    return jsonify(history)

# ===== COOKIE MANAGEMENT ROUTES =====

@app.route('/api/upload-cookies', methods=['POST'])
def upload_cookies():
    """Subir un archivo cookies.txt que se guarda persistentemente"""
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': 'No se recibiÃ³ ningÃºn archivo.'}), 400
    
    try:
        content = file.read().decode('utf-8', errors='ignore')
        # ValidaciÃ³n bÃ¡sica: debe contener al menos una lÃ­nea no-comentario
        valid_lines = [l for l in content.splitlines() if l.strip() and not l.startswith('#')]
        if not valid_lines:
            return jsonify({'error': 'El archivo no contiene cookies vÃ¡lidas.'}), 400
        
        with open(PERSISTENT_COOKIES_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Cookies saved: {len(valid_lines)} entries")
        return jsonify({'success': True, 'entries': len(valid_lines)})
    except Exception as e:
        logger.error(f"Cookie upload error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cookies-status', methods=['GET'])
def cookies_status():
    """Retorna si hay cookies cargadas"""
    exists = os.path.exists(PERSISTENT_COOKIES_FILE)
    entries = 0
    if exists:
        try:
            with open(PERSISTENT_COOKIES_FILE, 'r', encoding='utf-8') as f:
                entries = len([l for l in f.readlines() if l.strip() and not l.startswith('#')])
        except Exception:
            pass
    return jsonify({'has_cookies': exists, 'entries': entries})

@app.route('/api/cookies', methods=['DELETE'])
def delete_cookies():
    """Elimina las cookies guardadas"""
    if os.path.exists(PERSISTENT_COOKIES_FILE):
        os.remove(PERSISTENT_COOKIES_FILE)
    return jsonify({'status': 'ok'})

@app.route('/history/<download_id>', methods=['DELETE'])
def delete_history_route(download_id):
    history = load_history()
    new_history = [h for h in history if h.get('download_id') != download_id]
    with history_lock:
        _write_history_unlocked(new_history)
    return jsonify({'status': 'ok'})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    cookies_content = data.get('cookies')
    browser_source = data.get('browser') # 'brave', 'chrome', 'edge' or None

    # URL Normalization Fixes
    # Fix for YouPorn 'es.' subdomain not triggering YouPornIE in yt-dlp
    if 'youporn.com' in url:
        url = url.replace('es.youporn.com', 'www.youporn.com')
        logger.info(f"Normalized URL to: {url}")

    # Fix PornHub language subdomains (es., fr., de., etc.) -> www.
    if 'pornhub.com' in url:
        url = re.sub(r'https?://[a-z]{2}\.pornhub\.com', 'https://www.pornhub.com', url)
        logger.info(f"Normalized PornHub URL to: {url}")

    # Fix eporner language subdomains (es., fr., de., etc.) -> www.
    # yt-dlp's EpornerIE only matches www.eporner.com
    if 'eporner.com' in url:
        url = re.sub(r'https?://[a-z]{2}\.eporner\.com', 'https://www.eporner.com', url)
        logger.info(f"Normalized eporner URL to: {url}")

    logger.info(f"Analyze Request: URL={url}, Browser={browser_source}, CookiesLen={len(cookies_content) if cookies_content else 0}")

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    # Use extraction_url for site-specific fallbacks while preserving original URL for UI/history.
    extraction_url = url
    hqporner_candidates = []
    hqporner_iframe_url = None
    hqporner_provider_blocked = False

    session_id = str(uuid.uuid4())
    cookies_path = get_cookies_path(session_id)

    # --- ROBUST COOKIE EXTRACTION ---

    
    # --- EPORNER CUSTOM EXTRACTOR ---
    # yt-dlp's built-in EpornerIE works but fails on language subdomains (es., fr., etc.)
    # We replicate the same logic here for reliability + direct URL support.
    if 'eporner.com' in url:
        try:
            logger.info("Using Custom EPorner Extractor...")
            ep_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.eporner.com/'
            }

            # Extract video ID from URL (pattern: /video-{id}/ or /hd-porn/{id}/ or /embed/{id})
            vid_id_match = re.search(r'/(?:video-|hd-porn/|embed/)([A-Za-z0-9]+)', url)
            if not vid_id_match:
                raise Exception("No se pudo extraer el ID del video de la URL de eporner")
            vid_id = vid_id_match.group(1)
            logger.info(f"EPorner: Extracted video ID: {vid_id}")

            # Fetch video page
            page_resp = requests.get(url, headers=ep_headers, timeout=20)
            page_resp.raise_for_status()
            html = page_resp.text

            # Extract title
            title_match = re.search(r'<title>(.*?)</title>', html, re.DOTALL)
            video_title = title_match.group(1).strip() if title_match else "EPorner Video"
            # Clean common suffixes
            for suffix in [' - EPORNER', ' - Eporner', ' | EPORNER']:
                video_title = video_title.replace(suffix, '').strip()

            # Extract thumbnail
            thumb_match = re.search(r'property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', html)
            if not thumb_match:
                thumb_match = re.search(r'content=["\']([^"\']+)["\'][^>]*property=["\']og:image["\']', html)
            video_thumb = thumb_match.group(1) if thumb_match else ""

            # Extract duration
            dur_match = re.search(r'"duration"\s*:\s*"?PT?(\d+)M?(\d*)S?"?', html)
            duration = 0
            if dur_match:
                try:
                    mins = int(dur_match.group(1)) if dur_match.group(1) else 0
                    secs = int(dur_match.group(2)) if dur_match.group(2) else 0
                    duration = mins * 60 + secs
                except Exception: pass

            # Extract the hash needed for the API call
            # EPorner embeds a 32-char MD5-like hash in the page JS
            hash_match = re.search(r'hash\s*[:=]\s*["\']([a-f0-9]{32})["\']', html)
            if not hash_match:
                raise Exception("No se encontrÃ³ el hash de video en la pÃ¡gina de eporner")
            vid_hash = hash_match.group(1)
            logger.info(f"EPorner: Hash found: {vid_hash}")

            # Calculate API hash (reverse-engineered from eporner's vjs.js)
            def _encode_base36(num):
                TABLE = '0123456789abcdefghijklmnopqrstuvwxyz'
                if num == 0:
                    return '0'
                result = ''
                while num:
                    result = TABLE[num % 36] + result
                    num //= 36
                return result

            def _calc_eporner_hash(s):
                return ''.join(_encode_base36(int(s[lb:lb + 8], 16)) for lb in range(0, 32, 8))

            api_hash = _calc_eporner_hash(vid_hash)
            logger.info(f"EPorner: Calculated API hash: {api_hash}")

            # Call eporner XHR API
            api_resp = requests.get(
                f'https://www.eporner.com/xhr/video/{vid_id}',
                headers=ep_headers,
                params={
                    'hash': api_hash,
                    'device': 'generic',
                    'domain': 'www.eporner.com',
                    'fallback': 'false'
                },
                timeout=15
            )
            api_resp.raise_for_status()
            video_data = api_resp.json()

            if video_data.get('available') is False:
                msg = video_data.get('message', 'Video no disponible')
                raise Exception(f"EPorner dijo: {msg}")

            # Parse sources
            sources = video_data.get('sources', {})
            custom_formats = []

            for kind, formats_dict in sources.items():
                if not isinstance(formats_dict, dict):
                    continue
                for fmt_id, fmt_data in formats_dict.items():
                    if not isinstance(fmt_data, dict):
                        continue
                    src = fmt_data.get('src', '')
                    if not src or not src.startswith('http'):
                        continue

                    # Parse height from format label ("720p HD", "480p", "1080p", etc.)
                    height = 0
                    height_match = re.search(r'(\d+)[pP]', fmt_id)
                    if height_match:
                        height = int(height_match.group(1))

                    if kind == 'hls':
                        custom_formats.append({
                            'id': src,
                            'resolution': f'{height}p' if height else fmt_id,
                            'note': 'HLS',
                            'size': 'N/A',
                            'height': height,
                            'ext': 'mp4',
                            '_url': src
                        })
                    else:
                        custom_formats.append({
                            'id': src,
                            'resolution': f'{height}p' if height else fmt_id,
                            'note': 'MP4',
                            'size': 'N/A',
                            'height': height,
                            'ext': 'mp4',
                            '_url': src
                        })

            if not custom_formats:
                raise Exception("No se encontraron fuentes de video en la respuesta de la API de eporner")

            # Sort by quality (highest first)
            custom_formats.sort(key=lambda x: x['height'], reverse=True)

            logger.info(f"EPorner: Found {len(custom_formats)} formats: {[f['resolution'] for f in custom_formats]}")

            return jsonify({
                'type': 'video',
                'title': video_title,
                'thumbnail': video_thumb,
                'duration': duration,
                'uploader': 'EPorner',
                'formats': custom_formats,
                'session_id': session_id,
                'webpage_url': url,
                'cookie_warning': False,
                'is_direct': True
            })

        except Exception as e:
            logger.error(f"Custom EPorner extraction failed: {e}")
            logger.error(traceback.format_exc())
            # Fallthrough to yt-dlp as backup

    # --- PORNOXO CUSTOM EXTRACTOR ---
    # yt-dlp fails heavily on this site, so we implement a custom valid regex parser
    if 'pornoxo.com' in url:
        try:
            logger.info("Using Custom PornoXO Extractor...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.pornoxo.com/'
            }
            # Fetch page
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            html = resp.text
            
            # Extract Title
            title_match = re.search(r'<title>(.*?)</title>', html)
            video_title = title_match.group(1).split(" - PornoXO")[0] if title_match else "PornoXO Video"
            
            # Extract Thumbnail (Robust)
            # Try og:image first
            thumb_match = re.search(r'property=["\']og:image["\'].*?content=["\'](.*?)["\']', html)
            if not thumb_match:
                # Try twitter:image
                thumb_match = re.search(r'name=["\']twitter:image["\'].*?content=["\'](.*?)["\']', html)
            
            video_thumb = thumb_match.group(1) if thumb_match else ""

            # Extract Sources JSON
            # var sources = [{"src":"...","desc":"..."...}];
            sources_match = re.search(r'var sources = (\[.*?\]);', html)
            
            if sources_match:
                sources_json = sources_match.group(1)
                sources_data = json.loads(sources_json)
                
                custom_formats = []
                for s in sources_data:
                    # src key has the URL
                    s_url = s.get('src')
                    label = s.get('desc', 'Unknown') # 1080p, 720p
                    if not s_url: continue
                    
                    # Determine height from label (e.g. "1080p" -> 1080)
                    height = 0
                    try:
                        height = int(re.sub(r'\D', '', label))
                    except Exception: pass
                    
                    # Clean up URL (unicode escapes are handled by json.loads)
                    # Note: PornoXO URLs might need the Referer header during download
                    # Use URL as ID so frontend sends it back
                    
                    custom_formats.append({
                        'id': s_url, 
                        'resolution': label,
                        'note': 'Direct Link',
                        'size': 'N/A', 
                        'height': height,
                        'ext': 'mp4',
                        '_url': s_url, 
                    })
                
                if custom_formats:
                    # Sort
                    custom_formats.sort(key=lambda x: x['height'], reverse=True)
                    
                    # Generate Session ID
                    if not session_id: session_id = str(uuid.uuid4())
                    
                    return jsonify({
                        'type': 'video',
                        'title': video_title,
                        'thumbnail': video_thumb,
                        'duration': 0,
                        'uploader': 'PornoXO',
                        'formats': custom_formats,
                        'session_id': session_id,
                        'webpage_url': url,
                        'cookie_warning': False,
                        'is_direct': True # Hint for frontend or debugging
                    })
                    
        except Exception as e:
            logger.error(f"Custom PornoXO extraction failed: {e}")
            # Fallthrough to yt-dlp

    # Custom XNXX Extractor (to ensure Quality Options appear without Cookies)
    if 'xnxx.com' in url or 'xnxx.es' in url:
        try:
            logger.info("Using Custom XNXX Extractor")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            # Fetch page
            logger.info("XNXX: Fetching page HTML...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            html = response.text
            logger.info(f"XNXX: Received HTML ({len(html)} bytes)")
            
            # Extract Title
            title_match = re.search(r"html5player\.setVideoTitle\('([^']+)'\)", html)
            if not title_match:
                 title_match = re.search(r'<title>(.*?)</title>', html)
            
            video_title = title_match.group(1).replace(' - XNXX.COM', '').replace(' - XNXX.ES', '').strip() if title_match else "Unknown Title"
            logger.info(f"XNXX: Extracted title: {video_title}")
            
            # Extract Thumbnail
            thumb_match = re.search(r"html5player\.setThumbUrl169\('([^']+)'\)", html)
            if not thumb_match:
                thumb_match = re.search(r"html5player\.setThumbUrl\('([^']+)'\)", html)
            video_thumb = thumb_match.group(1) if thumb_match else ""
            logger.info(f"XNXX: Thumbnail found: {bool(video_thumb)}")
            
            # Extract Uploader/Actress Name
            uploader = None
            
            # Try to extract from JSON field "uploader"
            uploader_match = re.search(r'"uploader"\s*:\s*"([^"]+)"', html)
            if uploader_match:
                uploader = uploader_match.group(1)
                logger.info(f"XNXX: Found uploader from JSON: {uploader}")
            
            # Fallback: Try to find pornstar name from links
            if not uploader:
                pornstar_match = re.search(r'<a[^>]*href="/pornstar/([^/"]+)"', html, re.IGNORECASE)
                if pornstar_match:
                    uploader = pornstar_match.group(1)
                    logger.info(f"XNXX: Found uploader from pornstar link: {uploader}")
            
            # Default fallback
            if not uploader:
                uploader = "Unknown"
                logger.info(f"XNXX: No uploader found, using default: {uploader}")


            # Extract HLS URL (This is the key!)
            custom_formats = []
            hls_match = re.search(r"html5player\.setVideoHLS\('([^']+)'\)", html)
            
            if hls_match:
                hls_url = hls_match.group(1)
                logger.info(f"XNXX: Found HLS URL: {hls_url[:60]}...")
                
                try:
                    # Fetch HLS master playlist
                    logger.info("XNXX: Fetching HLS master playlist...")
                    hls_resp = requests.get(hls_url, headers=headers, timeout=15)
                    hls_resp.raise_for_status()
                    hls_content = hls_resp.text
                    logger.info(f"XNXX: HLS playlist size: {len(hls_content)} bytes")
                    
                    # Parse m3u8 master playlist
                    lines = hls_content.split('\n')
                    logger.info(f"XNXX: Parsing {len(lines)} lines from HLS playlist...")
                    
                    i = 0
                    while i < len(lines):
                        line = lines[i].strip()
                        
                        if line.startswith('#EXT-X-STREAM-INF:'):
                            # Extract resolution and bandwidth
                            resolution_match = re.search(r'RESOLUTION=(\d+)x(\d+)', line)
                            _bandwidth_match = re.search(r'BANDWIDTH=(\d+)', line)
                            
                            # Next line should be the playlist URL
                            if i + 1 < len(lines) and resolution_match:
                                playlist_url = lines[i + 1].strip()
                                
                                if playlist_url:
                                    width = int(resolution_match.group(1))
                                    height = int(resolution_match.group(2))
                                    
                                    # Construct full URL if relative
                                    if not playlist_url.startswith('http'):
                                        base_url = '/'.join(hls_url.split('/')[:-1])
                                        playlist_url = f"{base_url}/{playlist_url}"
                                    
                                    custom_formats.append({
                                        'id': playlist_url,  # Use the specific quality playlist URL
                                        'resolution': f'{height}p',
                                        'height': height,
                                        'width': width,
                                        'ext': 'mp4',
                                        'size': 'N/A',
                                        'note': 'HLS',
                                        '_url': playlist_url
                                    })
                                    logger.info(f"XNXX: Found quality: {height}p ({width}x{height})")
                        
                        i += 1
                    
                    logger.info(f"XNXX: Total qualities extracted: {len(custom_formats)}")
                    
                except Exception as hls_error:
                    logger.error(f"XNXX: Failed to parse HLS playlist: {hls_error}")
                    # Don't fail completely, try fallback methods below
            else:
                logger.warning("XNXX: HLS URL not found, trying fallback direct URLs...")
                
                # Fallback: Try old direct URL methods (might not exist on newer XNXX)
                high_match = re.search(r"html5player\.setVideoUrlHigh\('([^']+)'\)", html)
                if high_match:
                    high_url = high_match.group(1)
                    custom_formats.append({
                        'id': high_url,
                        'resolution': 'High Quality',
                        'height': 720,
                        'ext': 'mp4',
                        'size': 'N/A',
                        'note': 'MP4'
                    })
                    logger.info("XNXX: Found High Quality direct URL")
                    
                low_match = re.search(r"html5player\.setVideoUrlLow\('([^']+)'\)", html)
                if low_match:
                    low_url = low_match.group(1)
                    custom_formats.append({
                        'id': low_url,
                        'resolution': 'Low Quality',
                        'height': 360,
                        'ext': 'mp4',
                        'size': 'N/A',
                        'note': 'MP4'
                    })
                    logger.info("XNXX: Found Low Quality direct URL")

            # If manual extraction failed to find ANY video, fall back to yt-dlp
            if not custom_formats:
                 logger.warning("XNXX: Custom extraction found NO formats. Falling back to yt-dlp.")
            else:
                # Sort by quality (highest first)
                custom_formats.sort(key=lambda x: x['height'], reverse=True)
                
                # Add Session ID if missing
                if not session_id: session_id = str(uuid.uuid4())
                
                logger.info(f"XNXX: Returning {len(custom_formats)} formats to frontend")
                return jsonify({
                    'type': 'video',
                    'title': video_title,
                    'thumbnail': video_thumb,
                    'duration': 0,
                    'uploader': uploader,  # Use extracted uploader name
                    'formats': custom_formats,
                    'session_id': session_id,
                    'webpage_url': url,
                    'is_direct': True # Signal to run_download to skip yt-dlp analysis
                })

        except Exception as e:
            logger.error(f"Custom XNXX extraction failed: {e}")
            logger.error(f"XNXX Traceback: {traceback.format_exc()}")
            # Fallthrough to yt-dlp

    # HQPorner fallback: pages often embed video provider in iframe that generic extractor misses.
    if 'hqporner.com' in url:
        try:
            # Build canonical URL candidates to avoid false 404 on non-canonical slugs.
            hqporner_candidates = [url]
            m = re.search(r'hqporner\.com/hdporn/([^/?#]+)', url, re.IGNORECASE)
            if m:
                tail = m.group(1)
                tail_no_html = re.sub(r'\.html$', '', tail, flags=re.IGNORECASE)
                id_match = re.match(r'(\d+)', tail_no_html)

                if not tail_no_html.lower().endswith('.html'):
                    hqporner_candidates.append(f"https://hqporner.com/hdporn/{tail_no_html}.html")
                if id_match:
                    hqporner_candidates.append(f"https://hqporner.com/hdporn/{id_match.group(1)}")

            # Keep order while deduplicating.
            ordered = []
            seen = set()
            for candidate in hqporner_candidates:
                if candidate not in seen:
                    ordered.append(candidate)
                    seen.add(candidate)
            hqporner_candidates = ordered

            # Prefer canonical .html candidate first when available.
            html_candidate = next((c for c in hqporner_candidates if c.lower().endswith('.html')), None)
            if html_candidate:
                extraction_url = html_candidate

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://hqporner.com/'
            }
            resp = requests.get(extraction_url, headers=headers, timeout=20)
            resp.raise_for_status()
            html = resp.text

            iframe_match = re.search(r'<iframe[^>]+src=["\']([^"\']+)["\']', html, re.IGNORECASE)
            if iframe_match:
                iframe_url = iframe_match.group(1).strip()
                if iframe_url.startswith('//'):
                    iframe_url = f"https:{iframe_url}"
                elif iframe_url.startswith('/'):
                    iframe_url = f"https://hqporner.com{iframe_url}"

                logger.info(f"HQPorner fallback iframe detected: {iframe_url}")
                hqporner_iframe_url = iframe_url

                # If embed provider is blocked on the current network, return a clear message.
                try:
                    iframe_resp = requests.get(iframe_url, headers=headers, timeout=20)
                    iframe_text = iframe_resp.text.lower()
                    if 'this domain has been blocked' in iframe_text:
                        hqporner_provider_blocked = True
                        logger.warning('HQPorner embed provider appears blocked on current network/ISP')
                except Exception:
                    # Continue with yt-dlp fallback even if direct iframe probe fails.
                    pass
        except Exception as e:
            logger.warning(f"HQPorner fallback pre-check failed: {e}")

    # Build yt-dlp Command
    cmd = [sys.executable, '-m', 'yt_dlp', '--dump-json', '--verbose']
    
    # Modern Chrome User-Agent to avoid bot detection
    cmd.extend(['--impersonate', 'Chrome-110'])
    cmd.extend(['--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'])
    
    # Explicit Referer for sites that need it
    if 'youporn.com' in url:
        cmd.extend(['--referer', 'https://www.youporn.com/'])

    # --- COOKIE HANDLING ---
    # Priority: 1) Persistent cookies.txt, 2) Manual cookies pasted by user
    if os.path.exists(PERSISTENT_COOKIES_FILE):
        cmd.extend(['--cookies', PERSISTENT_COOKIES_FILE])
        logger.info("Analyze: Using persistent cookies file")
    elif cookies_content:
        # Sanitize Manual Cookies: Convert spaces to tabs if likely Netscape format
        try:
            sanitized_lines = []
            for line in cookies_content.splitlines():
                if not line.strip() or line.strip().startswith('#'):
                    sanitized_lines.append(line)
                    continue
                if '\t' not in line and ' ' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        domain = parts[0]
                        flag = parts[1]
                        path = parts[2]
                        secure = parts[3]
                        expiration = parts[4]
                        name = parts[5]
                        value = " ".join(parts[6:])
                        sanitized_lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
                    else:
                        sanitized_lines.append(line)
                else:
                    sanitized_lines.append(line)
            cookies_content = "\n".join(sanitized_lines)
            logger.info("Sanitized manual cookies (converted potential spaces to tabs)")
        except Exception as e:
            logger.warning(f"Cookie sanitization failed: {e}")

        with open(cookies_path, 'w', encoding='utf-8') as f:
            f.write(cookies_content)
        cmd.extend(['--cookies', cookies_path])
    
    # Remove 'generic:impersonate' as it might conflict with specific extractors
    # cmd.extend(['--extractor-args', 'generic:impersonate'])

    extract_targets = [extraction_url]
    if hqporner_candidates:
        for candidate in hqporner_candidates:
            if candidate not in extract_targets:
                extract_targets.append(candidate)
    if hqporner_iframe_url and hqporner_iframe_url not in extract_targets:
        extract_targets.append(hqporner_iframe_url)

    result = None
    last_error_msg = ''

    try:
        # Run subprocess with retries for site-specific candidate URLs.
        # INCREASED TIMEOUT: Browser cookie extraction can be slow
        for target in extract_targets:
            current_cmd = cmd + [target]
            logger.info(f"Executing command: {' '.join(current_cmd)}")
            current_result = subprocess.run(
                current_cmd,
                capture_output=True,
                text=True,
                timeout=45,
                encoding='utf-8',
                errors='ignore'
            )

            if current_result.returncode == 0:
                result = current_result
                extraction_url = target
                break

            current_error = current_result.stderr.strip() or current_result.stdout.strip() or "Unknown error (process failed)"
            last_error_msg = current_error
            logger.warning(f"yt-dlp failed for target {target}: {current_error}")

        if result is None:
            error_msg = last_error_msg or "Unknown error (process failed)"

            # Helper for browser lock
            if "cookie" in error_msg.lower() and ("copy" in error_msg.lower() or "lock" in error_msg.lower() or "permission" in error_msg.lower()):
                clean_error = "Error de Cookies: El navegador estÃ¡ bloqueado. Por favor cierra el navegador o usa el 'Modo Manual' para pegar cookies."
            elif hqporner_provider_blocked:
                clean_error = (
                    'HQPorner carga este video mediante un proveedor embebido no compatible o bloqueado en esta red. '
                    'Prueba con otra red/VPN o usa otro enlace del sitio.'
                )
            else:
                clean_error = sanitize_ytdlp_error(error_msg, source_url=url)

            return jsonify({'error': clean_error}), 500

        # Parse JSON
        info = json.loads(result.stdout)

        # Detect Playlist (CLI valid json usually has '_type': 'playlist' or 'entries')
        if info.get('_type') == 'playlist' or 'entries' in info:
            entries = []
            # 'entries' might be an iterator in python lib, but in JSON dump it's a list
            for entry in info.get('entries', []):
                if not entry: continue
                entries.append({
                    'id': entry.get('id'),
                    'title': entry.get('title', 'Unknown'),
                    'url': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}",
                    'duration': entry.get('duration', 0),
                    'thumbnail': entry.get('thumbnail', ''),
                    'uploader': entry.get('uploader', 'Unknown')
                })
            
            return jsonify({
                'type': 'playlist',
                'title': info.get('title', 'Playlist'),
                'entries': entries,
                'session_id': session_id,
                'webpage_url': info.get('webpage_url', url)
            })

        # Single Video Logic
        title = info.get('title', 'Unknown Title')
        thumbnail = info.get('thumbnail', '')
        duration = info.get('duration', 0)
        webpage_url = info.get('webpage_url', url)
        
        # Enhanced Uploader Detection
        # Try to find a meaningful name for the folder
        uploader = info.get('uploader')
        if not uploader or uploader == 'Unknown':
            uploader = info.get('creator') or info.get('channel') or info.get('uploader_id')
        
        # FALLBACK: Extract from title or URL if still unknown
        # Many sites like xgroovy.com embed the actress/pornstar name in the title or URL
        if not uploader:
            # Common pornstar/actress first names to help identify valid names
            common_actress_names = ['sia', 'angela', 'mia', 'riley', 'abella', 'lana', 'kendra', 
                                   'alexis', 'brandi', 'nicole', 'lisa', 'anna', 'emma', 'megan',
                                   'dani', 'jenna', 'madison', 'adriana', 'ava', 'luna', 'elsa']
            
            # Method 1: Try lowercase names from title first (most reliable for matching known names)
            # Look for patterns like "actriz nombre" in lowercase
            lowercase_pattern = r'\b([a-z]{3,12}\s+[a-z]{3,12}(?:\s+[a-z]{3,12})?)\b'
            matches = re.findall(lowercase_pattern, title.lower())
            
            if matches:
                for match in matches:
                    # Check if any common name pattern is in the match
                    if any(pattern in match for pattern in common_actress_names):
                        # Capitalize it
                        uploader = ' '.join(word.capitalize() for word in match.split())
                        logger.info(f"Extracted uploader from title (lowercase pattern): {uploader}")
                        break
            
            # Method 2: Check URL slug (often contains the name)
            if not uploader:
                # Example: "...sia-siberia-and..." -> "Sia Siberia"
                url_slug = webpage_url.split('/')[-2] if '/' in webpage_url else ''
                if url_slug:
                    # Look for name patterns in URL (dash-separated words)
                    slug_words = url_slug.replace('-', ' ').split()
                    
                    # Find consecutive capitalized-looking words (2-3 words)
                    for i in range(len(slug_words) - 1):
                        potential_name = ' '.join(slug_words[i:min(i+3, len(slug_words))])
                        # Capitalize each word
                        potential_name = ' '.join(word.capitalize() for word in potential_name.split())
                        
                        # Check if it looks like a name (2-3 words, reasonable length)
                        words = potential_name.split()
                        if 2 <= len(words) <= 3 and all(3 <= len(w) <= 15 for w in words):
                            # Expanded list of generic/descriptive words to exclude
                            generic_slugs = ['hot', 'sexy', 'video', 'watch', 'free', 'online', 'download',
                                           'best', 'new', 'latest', 'top', 'full', 'hd', 'porn', 'xxx',
                                           'anal', 'oral', 'solo', 'lesbian', 'threesome', 'amateur', 'big',
                                           'busty', 'slim', 'skinny', 'thick', 'curvy', 'petite', 'tall',
                                           'beauty', 'babe', 'girl', 'woman', 'teen', 'milf', 'mature',
                                           'blonde', 'brunette', 'redhead', 'asian', 'ebony', 'latina',
                                           'young', 'old', 'cute', 'beautiful', 'gorgeous', 'delgada',
                                           'tetona', 'caliente', 'bella', 'hermosa', 'joven']
                            
                            if not any(word.lower() in generic_slugs for word in words):
                                # Additional check: prefer if it contains a known actress name
                                if any(name in potential_name.lower() for name in common_actress_names):
                                    uploader = potential_name
                                    logger.info(f"Extracted uploader from URL slug (matched known name): {uploader}")
                                    break
                                elif i > len(slug_words) // 2:  # Prefer names in second half of URL
                                    uploader = potential_name
                                    logger.info(f"Extracted uploader from URL slug: {uploader}")
                                    break
            
            
            # Method 3: Extract from title - Try capitalized names
            if not uploader:
                # Pattern: Find sequences of capitalized words (potential names)
                name_patterns = [
                    # Match 2-3 capitalized words (e.g., "Sia Siberia", "Angela White")
                    r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b',
                ]
                
                for pattern in name_patterns:
                    matches = re.findall(pattern, title)
                    if matches:
                        # Use the first match as potential uploader
                        potential_uploader = matches[0]
                        # Avoid generic words
                        generic_words = ['Video', 'Hot', 'Best', 'New', 'Top', 'Full', 'Hd', 'Complete',
                                       'Premium', 'Quality', 'Online', 'Free', 'Download', 'Watch']
                        
                        words = potential_uploader.split()
                        if not any(word in generic_words for word in words):
                            uploader = potential_uploader
                            logger.info(f"Extracted uploader from title (capitalized): {uploader}")
                            break

        
        # YouPorn Specific: sometimes 'categories' or 'tags' have the actor name, but it's hard to distinguish.
        # We will stick to standard fields first.
        
        if not uploader:
             uploader = 'Unknown'
             
        logger.info(f"Metadata Extracted: Title='{title}', Uploader='{uploader}' (Extractor: {info.get('extractor')})")
        # Debug: Log all keys to see if we missed something useful
        logger.info(f"Available Metadata Keys: {list(info.keys())}")
        
        unique_formats = {}
        for f in info.get('formats', []):
            # ... (Rest of format loop) ...
            # Skip only if explicitly audio-only (vcodec='none') AND acodec exists
            # VirtualTaboo returns vcodec=None, which is fine to keep.
            # Relaxed Filtering: Allow Audio-Only and Unknown Height
            is_video = f.get('vcodec') != 'none'
            is_audio = f.get('acodec') != 'none'
            
            height = f.get('height')
            
            # Setup "Safe" Height for Grouping
            if height is None:
                # If height is missing, check if it's likely a video container
                if f.get('ext') in ['mp4', 'mkv', 'webm', 'mov']:
                    height = 0 # Treated as "Unknown"
                elif is_audio and not is_video:
                     height = 0 # Audio tracks
                else:
                     continue # Skip unknown non-media things
            
            # Allow 0 height (Unknown/Audio) to pass. 
            # Only filter out tiny video thumbnails if we are sure they are video
            if is_video and height > 0 and height < 144: continue 
            
            resolution = f.get('resolution') or f"{f.get('width', '?')}x{f.get('height', '?')}"
            if resolution == "?x?": resolution = "Original / Unknown"
            
            # Label Audio Only
            if not is_video and is_audio:
                resolution = "ðŸŽµ Audio Only"
                height = 0 # Ensure it groups together
            
            filesize = f.get('filesize') or f.get('filesize_approx') or 0
            
            existing = unique_formats.get(height)
            if existing:
                existing_size = existing.get('_raw_size', 0)
                # Keep the larger file (usually better quality)
                if filesize > existing_size:
                    unique_formats[height] = {
                        'id': f['format_id'],
                        'resolution': resolution,
                        'note': f.get('format_note', ''),
                        'size': format_bytes(filesize) if filesize else "N/A",
                        'height': height,
                        'ext': f.get('ext'),
                        '_raw_size': filesize
                    }
            else:
                unique_formats[height] = {
                    'id': f['format_id'],
                    'resolution': resolution,
                    'note': f.get('format_note', ''),
                    'size': format_bytes(filesize) if filesize else "N/A",
                    'height': height,
                    'ext': f.get('ext'),
                    '_raw_size': filesize
                }

        if not unique_formats:
             logger.warning(f"No formats passed filter. Raw formats count: {len(info.get('formats', []))}")
             # DUMP FULL STDERR to see yt-dlp warnings (e.g. Login Required/Extractor Error)
             logger.error("Dumping full yt-dlp stderr due to missing formats:")
             logger.error(result.stderr)
             
             # Dump first 10 raw formats to see what's wrong
             for i, rf in enumerate(info.get('formats', [])[:10]):
                 logger.info(f"Raw Format {i}: id={rf.get('format_id')}, ext={rf.get('ext')}, vcodec={rf.get('vcodec')}, acodec={rf.get('acodec')}, h={rf.get('height')}, res={rf.get('resolution')}")

        formats = list(unique_formats.values())
        formats.sort(key=lambda x: x['height'], reverse=True)

        return jsonify({
            'type': 'video', 
            'title': title,
            'thumbnail': thumbnail,
            'duration': duration,
            'uploader': uploader, # Use our enhanced uploader
            'formats': formats,
            'session_id': session_id,
            'webpage_url': webpage_url,
            'cookie_warning': False
        })

    except subprocess.TimeoutExpired:
        if os.path.exists(cookies_path): os.remove(cookies_path)
        return jsonify({'error': 'Tiempo de espera agotado. El navegador tardÃ³ demasiado en responder.'}), 504
    except Exception as e:
        logger.error(f"Error in extract_info subprocess: {e}")
        if os.path.exists(cookies_path): os.remove(cookies_path)
        clean_error = re.sub(r'\x1b\[[0-9;]*m', '', str(e))
        return jsonify({'error': clean_error}), 500


def run_download(url, format_id, session_id, download_id, metadata, browser_source=None, force=False):
    cookies_path = get_cookies_path(session_id)

    # Save/update history entry
    metadata['download_id'] = download_id
    metadata['status'] = 'starting'
    metadata.setdefault('timestamp', str(datetime.datetime.now()))
    # Ensure default fields
    metadata.setdefault('title', 'Unknown')
    metadata.setdefault('thumbnail', '')
    metadata.setdefault('duration', 0)

    save_history_entry(metadata)

    # Unique temp dir for THIS download to avoid collision/locking
    unique_temp = os.path.join(os.environ.get('TEMP', '.'), 'yt_dlp_temp', download_id)

    # Internal Hook to check abort signal
    def check_abort(d):
        if abort_signals.get(download_id):
            raise Exception("PAUSED_BY_USER")
    
    # Normalize Uploader name to avoid duplicate folders (e.g., "Karneli_Bandi" and "Karneli Bandi")
    uploader_folder = normalize_uploader_name(metadata.get('uploader', 'Unknown'))
    
    # If uploader is Unknown, use site name as fallback
    if uploader_folder == 'Unknown':
        site_name = get_site_name(url)
        if site_name != 'Unknown Site':
            uploader_folder = site_name

    # Direct Download Check (Custom Extractors)
    is_direct_url = format_id.startswith('http')
    
    # Base configuration
    ydl_opts = {
        # Use explicit uploader folder from our metadata, but let yt-dlp name the file
        'outtmpl': os.path.join(TEMP_DOWNLOADS_DIR, uploader_folder, '%(title)s.%(ext)s'), 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'impersonate': ImpersonateTarget.from_str('Chrome-110'),
        # 'referer': 'https://www.youporn.com/', # REMOVED global referer logic
        'progress_hooks': [check_abort], 
        'restrictfilenames': True,
        'paths': {'temp': unique_temp},
        'overwrites': force,
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        # --- Velocidad mÃ¡xima: descarga concurrente de fragmentos (HLS/DASH) ---
        'concurrent_fragment_downloads': 16,  # 16 hilos paralelos para fragmentos
        'http_chunk_size': 10 * 1024 * 1024,  # Chunks de 10MB para conexiones rÃ¡pidas
        'buffersize': 1024 * 16,              # Buffer de red de 16KB
    }

    if FFMPEG_LOCATION:
        ydl_opts['ffmpeg_location'] = FFMPEG_LOCATION

    mode = metadata.get('mode', 'video')

    if is_direct_url:
        # If format_id is a URL, it's a direct stream link (m3u8/mp4)
        target_url = format_id
        # We don't filter formats for direct links
    else:
        target_url = url
        if mode == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    },
                    {'key': 'FFmpegMetadata'}, # Add Metadata
                    {'key': 'EmbedThumbnail'}, # Embed Cover Art
                ],
            })
        else:
            ydl_opts.update({
                 'format': f"{format_id}+bestaudio/best",
                 'merge_output_format': 'mp4',
            })
    
    # Create temp dir if not exists
    os.makedirs(unique_temp, exist_ok=True)
    
    # Use persistent cookies if available (uploaded once via /api/upload-cookies)
    if os.path.exists(PERSISTENT_COOKIES_FILE):
        ydl_opts['cookiefile'] = PERSISTENT_COOKIES_FILE
        logger.info("Using persistent cookies for download")
    elif os.path.exists(cookies_path):
        # Fallback: per-session cookies from manual paste
        ydl_opts['cookiefile'] = cookies_path

    class IDHook:
        def __init__(self, dl_id):
            self.dl_id = dl_id
        def __call__(self, d):
            d['info_dict']['_download_id'] = self.dl_id
            progress_hook(d)

    ydl_opts['progress_hooks'] = [IDHook(download_id)]

    try:
        set_download_progress(download_id, {'status': 'starting', 'percent': '0%', 'speed': '0'})
        
        # Force Clean: Delete if exists and force is True
        if force:
            pass

        transient_markers = ['timed out', 'timeout', 'connection reset', 'temporarily unavailable', 'http error 429']
        max_attempts = 2
        last_error = None

        for attempt in range(1, max_attempts + 1):
            try:
                if attempt > 1:
                    set_download_progress(download_id, {
                        'status': 'retrying',
                        'percent': '0%',
                        'speed': f'Reintentando ({attempt}/{max_attempts})...'
                    })
                    time.sleep(1.5 * (attempt - 1))

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([target_url])
                last_error = None
                break
            except Exception as inner_exc:
                last_error = inner_exc
                err_lower = str(inner_exc).lower()
                if "PAUSED_BY_USER" in str(inner_exc):
                    raise
                if attempt >= max_attempts or not any(marker in err_lower for marker in transient_markers):
                    raise
                logger.warning(f"Transient download error ({attempt}/{max_attempts}) for {download_id}: {inner_exc}")

        if last_error is not None:
            raise last_error
            
        # Get final filename and size from progress
        final_info = download_progress.get(download_id, {})
        final_filename = final_info.get('filename')
        
        # Heuristic for final size if available
        final_total = final_info.get('total', '??')

        # Update specific fields in history BEFORE signaling finished to UI
        with history_lock:
            history = _load_history_unlocked()
            for item in history:
                if item.get('download_id') == download_id:
                    item['status'] = 'completed'
                    item['file_path'] = final_filename
                    item['size_str'] = final_total
                    break
            _write_history_unlocked(history)

        # Signal completion to UI and set 100%
        set_download_progress(download_id, {
            'total': final_total,
            'percent': '100%',
            'status': 'finished'
        })
        
    except Exception as e:
        err_msg = str(e)
        logger.error(f"Download Error Traceback: {traceback.format_exc()}")

        # WinError 32 handling: If we are in 'processing' state, it might be a cleanup error.
        # If the file exists, we might declare victory.
        is_win_error_32 = "[WinError 32]" in err_msg or (isinstance(e, OSError) and e.winerror == 32)
        
        # Check if we were already processing (means download finished, failure is likely in merge/cleanup)
        current_status = download_progress.get(download_id, {}).get('status')
        
        if is_win_error_32 and current_status == 'processing':
            logger.warning(f"Ignored WinError 32 during processing/cleanup for {download_id}: {err_msg}")
            # Try to assume success
            set_download_progress(download_id, {'status': 'finished', 'percent': '100%'})
            # Update history too
            update_history_status(download_id, 'completed_with_warning')
        elif "PAUSED_BY_USER" in err_msg:
             set_download_progress(download_id, {'status': 'paused', 'percent': 'PAUSADO', 'speed': '0'})
             update_history_status(download_id, 'paused')
        else:
            # Clean ANSI codes
            clean_error = re.sub(r'\x1b\[[0-9;]*m', '', err_msg)
            set_download_progress(download_id, {'status': 'error', 'error': clean_error})
            update_history_status(download_id, 'failed')
    finally:
        # Cleanup cookies if they were temp
        if os.path.exists(cookies_path) and not browser_source:
             try:
                 os.remove(cookies_path)
             except Exception: pass
        
        # Cleanup unique temp dir ONLY if NOT paused
        if download_progress.get(download_id, {}).get('status') != 'paused':
            for _ in range(5): # Retry loop
                try:
                    # shutil already imported at top-level
                    if os.path.exists(unique_temp):
                        shutil.rmtree(unique_temp)
                    break 
                except Exception as e:
                    logger.warning(f"Cleanup retry failed: {e}")
                    time.sleep(1.0)

def _on_download_done(download_id, future):
    with download_state_lock:
        download_futures.pop(download_id, None)

    if future.cancelled():
        set_download_progress(download_id, {
            'status': 'cancelled',
            'percent': '0%',
            'speed': 'Cancelado antes de iniciar'
        })
        update_history_status(download_id, 'cancelled')
        return

    exc = future.exception()
    if exc:
        logger.error(f"Unhandled worker exception for {download_id}: {exc}")
        set_download_progress(download_id, {
            'status': 'error',
            'error': str(exc)
        })
        update_history_status(download_id, 'failed')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    format_id = data.get('format_id')
    session_id = data.get('session_id')
    metadata = data.get('metadata', {}) 
    browser = data.get('browser') # Get browser choice
    force = data.get('force', False)
    
    if not url or not format_id:
        return jsonify({'error': 'Missing parameters'}), 400

    # URL Normalization (Same as Analyze)
    if 'youporn.com' in url:
        url = url.replace('es.youporn.com', 'www.youporn.com')
        logger.info(f"Normalized Download URL to: {url}")

    # Fix PornHub language subdomains (es., fr., de., etc.) -> www.
    if 'pornhub.com' in url:
        url = re.sub(r'https?://[a-z]{2}\.pornhub\.com', 'https://www.pornhub.com', url)
        logger.info(f"Normalized PornHub Download URL to: {url}")

    # Optional: Check for running downloads? 
    # Duplicate check happens in Frontend before calling this, or here.
    # We'll just launch.
    
    download_id = data.get('download_id') or str(uuid.uuid4())
    
    # Reset abort signal for this ID
    if download_id in abort_signals:
        del abort_signals[download_id]

    metadata = metadata if isinstance(metadata, dict) else {}
    metadata['download_id'] = download_id
    metadata.setdefault('title', 'Unknown')
    metadata.setdefault('thumbnail', '')
    metadata.setdefault('duration', 0)
    metadata['status'] = 'queued'
    metadata.setdefault('timestamp', str(datetime.datetime.now()))

    save_history_entry(metadata)

    set_download_progress(download_id, {
        'status': 'queued',
        'percent': '0%',
        'speed': 'En cola...',
        'file_path': None
    })

    with download_state_lock:
        future = download_executor.submit(run_download, url, format_id, session_id, download_id, metadata, browser, force)
        download_futures[download_id] = future
        future.add_done_callback(lambda f, did=download_id: _on_download_done(did, f))

    queue_stats = get_queue_stats()
    return jsonify({'status': 'queued', 'download_id': download_id, 'queue': queue_stats})

@app.route('/pause/<download_id>', methods=['POST'])
def pause_download(download_id):
    with download_state_lock:
        future = download_futures.get(download_id)
        if future and future.cancel():
            set_download_progress(download_id, {
                'status': 'cancelled',
                'percent': '0%',
                'speed': 'Cancelado antes de iniciar'
            })
            update_history_status(download_id, 'cancelled')
            return jsonify({'status': 'cancelled'})

    abort_signals[download_id] = True
    return jsonify({'status': 'pausing'})

@app.route('/download_file/<download_id>', methods=['GET'])
def download_file_route(download_id):
    history = load_history()
    item = next((h for h in history if h.get('download_id') == download_id), None)
    
    file_path = None
    if item and item.get('file_path'):
        file_path = item['file_path']
    
    # Fallback to in-memory progress if history failed or is slow
    if not file_path:
        prog = download_progress.get(download_id)
        if prog and prog.get('filename'):
            file_path = prog.get('filename')

    if not file_path:
        return "File path not found (History/Memory)", 404
    # If absolute path not saved, assume cwd
    if not os.path.isabs(file_path):
        file_path = os.path.abspath(file_path)
        
    if not os.path.exists(file_path):
        return "File deleted or moved", 404
        
    # DELETE-ON-SAVE Implementation
    @after_this_request
    def remove_file(response):
        if not _is_within_path(file_path, TEMP_DOWNLOADS_DIR):
            return response
        try:
            os.remove(file_path)
            logger.info(f"Deleted file after download: {file_path}")
            # Optional: Update history status to 'saved' or 'deleted'
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
        return response

    return send_file(file_path, as_attachment=True)

@app.route('/progress/<download_id>')
def progress(download_id):
    status = download_progress.get(download_id)
    if not status:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(status)

@app.route('/queue/status', methods=['GET'])
def queue_status():
    return jsonify(get_queue_stats())

@app.route('/health', methods=['GET'])
def health():
    queue = get_queue_stats()
    writable_download_dir = os.access(TEMP_DOWNLOADS_DIR, os.W_OK)
    history_exists = os.path.exists(HISTORY_FILE)

    return jsonify({
        'status': 'ok',
        'time': str(datetime.datetime.now()),
        'python': sys.version,
        'download_dir': TEMP_DOWNLOADS_DIR,
        'download_dir_writable': writable_download_dir,
        'history_file': HISTORY_FILE,
        'history_exists': history_exists,
        'ffmpeg_location': FFMPEG_LOCATION,
        'ffmpeg_available': bool(FFMPEG_LOCATION),
        'queue': queue,
    })


# ===== CLEANUP THREAD =====
# Automatically delete temp files older than 2 hours

CLEANUP_INTERVAL_SECONDS = 30 * 60  # 30 minutes
CLEANUP_MAX_AGE_SECONDS = 2 * 60 * 60  # 2 hours

def cleanup_old_files():
    """Background thread that cleans up old temporary download files."""
    while True:
        time.sleep(CLEANUP_INTERVAL_SECONDS)
        try:
            now = time.time()
            cleaned = 0
            for root, dirs, files in os.walk(TEMP_DOWNLOADS_DIR):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    try:
                        age = now - os.path.getmtime(fpath)
                        if age > CLEANUP_MAX_AGE_SECONDS:
                            os.remove(fpath)
                            cleaned += 1
                            logger.info(f"Cleanup: Deleted old file {fname} (age: {age/3600:.1f}h)")
                    except Exception as e:
                        logger.warning(f"Cleanup: Could not delete {fname}: {e}")
                
                # Remove empty subdirectories
                for dname in dirs:
                    dpath = os.path.join(root, dname)
                    try:
                        if not os.listdir(dpath):
                            os.rmdir(dpath)
                            logger.info(f"Cleanup: Removed empty dir {dname}")
                    except Exception:
                        pass
            
            if cleaned > 0:
                # Update history: mark entries whose files no longer exist as 'expired'
                with history_lock:
                    history = _load_history_unlocked()
                    updated = False
                    for item in history:
                        fp = item.get('file_path', '')
                        if fp and not os.path.exists(fp) and item.get('status') == 'completed':
                            item['status'] = 'expired'
                            updated = True
                    if updated:
                        _write_history_unlocked(history)
                
                logger.info(f"Cleanup: Removed {cleaned} expired files")
        except Exception as e:
            logger.error(f"Cleanup thread error: {e}")

# Start cleanup thread
cleanup_thread = threading.Thread(target=cleanup_old_files, daemon=True, name='cleanup-worker')
cleanup_thread.start()

if __name__ == '__main__':
    print("Iniciando V128 Downloader en http://0.0.0.0:5000")
    try:
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    except ImportError:
        # Fallback to Flask dev server if waitress not installed
        logger.warning("Waitress not installed. Using Flask dev server (not for production)")
        app.run(debug=True, host='0.0.0.0', port=5000)


