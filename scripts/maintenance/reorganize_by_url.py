"""
Script avanzado de reorganización usando URLs
Extrae información de uploader desde las URLs de los videos
"""

import json
import shutil
from pathlib import Path
import re
from urllib.parse import urlparse, unquote

def normalize_uploader_name(uploader):
    """Normaliza el nombre del uploader"""
    if not uploader or uploader == 'Unknown':
        return 'Unknown'
    
    name = uploader.replace('_', ' ').replace('-', ' ')
    name = "".join([c for c in name if c.isalnum() or c in (' ',)]).strip()
    name = ' '.join(word.capitalize() for word in name.split())
    
    if not name:
        return 'Unknown'
    
    return name

def extract_uploader_from_url(url):
    """
    Extrae el nombre del uploader desde la URL del video
    Soporta múltiples patrones de diferentes sitios
    """
    if not url:
        return None
    
    url_lower = url.lower()
    
    # XNXX - formato: /pornstar/nombre-uploader/
    xnxx_match = re.search(r'/pornstar/([^/]+)', url_lower)
    if xnxx_match:
        uploader = unquote(xnxx_match.group(1))
        uploader = uploader.replace('-', ' ')
        return normalize_uploader_name(uploader)
    
    # XNXX - formato: /channels/nombre-channel
    xnxx_channel = re.search(r'/channels?/([^/]+)', url_lower)
    if xnxx_channel:
        uploader = unquote(xnxx_channel.group(1))
        uploader = uploader.replace('-', ' ')
        return normalize_uploader_name(uploader)
    
    # XVideos - formato: /profiles/nombre-uploader
    xvideos_match = re.search(r'/profiles?/([^/]+)', url_lower)
    if xvideos_match:
        uploader = unquote(xvideos_match.group(1))
        uploader = uploader.replace('-', ' ')
        return normalize_uploader_name(uploader)
    
    # Pornhub - formato: /model/nombre o /pornstar/nombre
    pornhub_match = re.search(r'/(model|pornstar)/([^/]+)', url_lower)
    if pornhub_match:
        uploader = unquote(pornhub_match.group(2))
        uploader = uploader.replace('-', ' ')
        return normalize_uploader_name(uploader)
    
    # Pornhub - formato: /users/nombre
    pornhub_user = re.search(r'/users?/([^/]+)', url_lower)
    if pornhub_user:
        uploader = unquote(pornhub_user.group(1))
        uploader = uploader.replace('-', ' ')
        return normalize_uploader_name(uploader)
    
    # XGroovy - formato similar a XNXX
    if 'xgroovy' in url_lower:
        groovy_match = re.search(r'/(pornstar|channel|model)/([^/]+)', url_lower)
        if groovy_match:
            uploader = unquote(groovy_match.group(2))
            uploader = uploader.replace('-', ' ')
            return normalize_uploader_name(uploader)
    
    # Patrón genérico: /uploader/nombre o /user/nombre
    generic_match = re.search(r'/(uploader|user|creator|artist)/([^/]+)', url_lower)
    if generic_match:
        uploader = unquote(generic_match.group(2))
        uploader = uploader.replace('-', ' ')
        return normalize_uploader_name(uploader)
    
    return None

def get_site_name(url):
    """Extrae el nombre del sitio desde la URL"""
    if not url:
        return 'Unknown Site'
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # Limpiar dominio
    domain = domain.replace('www.', '')
    
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
    
    # Si no está en el mapa, usar dominio principal
    parts = domain.split('.')
    if len(parts) >= 2:
        return parts[-2].capitalize()
    
    return 'Unknown Site'

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "url_reorganize_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("REORGANIZACION AVANZADA USANDO URLs")
log("="*70)

log("\n[1/4] Cargando historial...")
with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

# Filtrar Unknown/NA
unknown_entries = [e for e in history if e.get('uploader', '').lower() in ['unknown', 'na', 'desconocido']]

log(f"      Total entradas Unknown: {len(unknown_entries)}")

log("\n[2/4] Analizando URLs...")

updates = []
for entry in unknown_entries:
    url = entry.get('original_url', '') or entry.get('url', '')  # Try both fields
    title = entry.get('title', '')[:60]
    file_path = entry.get('file_path', '')
    
    # Intentar extraer uploader desde URL
    uploader = extract_uploader_from_url(url)
    
    if uploader and uploader != 'Unknown':
        updates.append({
            'entry': entry,
            'new_uploader': uploader,
            'source': 'URL',
            'title': title,
            'file_path': file_path
        })
    else:
        # Si no se puede extraer uploader, usar nombre del sitio
        site_name = get_site_name(url)
        if site_name != 'Unknown Site':
            updates.append({
                'entry': entry,
                'new_uploader': f"{site_name} Videos",
                'source': 'Site',
                'title': title,
                'file_path': file_path
            })

log(f"      Uploaders extraidos de URL: {sum(1 for u in updates if u['source'] == 'URL')}")
log(f"      Clasificados por sitio: {sum(1 for u in updates if u['source'] == 'Site')}")
log(f"      Total reorganizables: {len(updates)}")

if not updates:
    log("\nNo se encontraron URLs validas para reorganizar")
else:
    # Agrupar por uploader
    by_uploader = {}
    for update in updates:
        uploader = update['new_uploader']
        if uploader not in by_uploader:
            by_uploader[uploader] = []
        by_uploader[uploader].append(update)
    
    log(f"\n[3/4] Carpetas a crear/usar: {len(by_uploader)}")
    log("-"*70)
    
    for uploader, items in sorted(by_uploader.items()):
        source_types = set(item['source'] for item in items)
        source_str = ', '.join(source_types)
        log(f"\n  {uploader} ({len(items)} archivos) [{source_str}]")
        
        for item in items[:3]:
            log(f"    - {item['title']}")
        if len(items) > 3:
            log(f"    ... y {len(items) - 3} mas")
    
    log("\n[4/4] Reorganizando archivos...")
    
    success_count = 0
    error_count = 0
    created_folders = set()
    
    for update in updates:
        entry = update['entry']
        new_uploader = update['new_uploader']
        file_path = Path(update['file_path']) if update['file_path'] else None
        
        # Actualizar historial
        entry['uploader'] = new_uploader
        
        # Si el archivo existe, moverlo
        if file_path and file_path.exists():
            # Crear carpeta
            uploader_folder = TEMP_DOWNLOADS / new_uploader
            uploader_folder.mkdir(exist_ok=True)
            created_folders.add(new_uploader)
            
            # Nueva ruta
            new_path = uploader_folder / file_path.name
            
            # Manejar duplicados
            if new_path.exists():
                stem = new_path.stem
                suffix = new_path.suffix
                counter = 1
                while new_path.exists():
                    new_path = uploader_folder / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            try:
                shutil.move(str(file_path), str(new_path))
                entry['file_path'] = str(new_path)
                log(f"  OK: {file_path.name[:45]} -> {new_uploader}/")
                success_count += 1
            except Exception as e:
                log(f"  ERROR: {file_path.name[:35]}: {str(e)[:25]}")
                error_count += 1
    
    # Guardar historial
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    log("\n" + "="*70)
    log("RESUMEN")
    log("="*70)
    log(f"Entradas analizadas: {len(unknown_entries)}")
    log(f"Nuevas carpetas creadas: {len(created_folders)}")
    log(f"Archivos reorganizados: {success_count}")
    log(f"Errores: {error_count}")
    log(f"Permanecen Unknown: {len(unknown_entries) - len(updates)}")
    
    log("\nCarpetas creadas:")
    for folder in sorted(created_folders):
        count = sum(1 for u in updates if u['new_uploader'] == folder)
        log(f"  - {folder} ({count} archivos)")
    
    if success_count > 0:
        log("\nEXITO: Reorganizacion completada")
        log("  -> Recarga la pagina web (F5) para ver los cambios")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
