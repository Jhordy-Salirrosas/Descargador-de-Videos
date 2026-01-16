"""
Script DEFINITIVO de reorganización - Combina análisis de título + scraping de URLs
"""

import json
import shutil
from pathlib import Path
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import time

def normalize_uploader_name(uploader):
    """Normaliza el nombre del uploader"""
    if not uploader or uploader == 'Unknown':
        return 'Unknown'
    
    name = uploader.replace('_', ' ').replace('-', ' ')
    name = "".join([c for c in name if c.isalnum() or c in (' ',)]).strip()
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name if name else 'Unknown'

def extract_actress_from_title_enhanced(title):
    """Extracción mejorada de nombres de actrices desde títulos"""
    if not title:
        return None
    
    # Limpiar título
    title_clean = title.replace('(1)', '').replace('(2)', '').strip()
    
    # Lista expandida de nombres conocidos
    known_patterns = {
        r'sia\s+siberia': 'Sia Siberia',
        r'karneli\s+bandi': 'Karneli Bandi',
        r'lexi\s+lore': 'Lexi Lore',
        r'molly\s*red\s*wolf': 'Molly Redwolf',
        r'julie\s+jess': 'Julie Jess',
        r'angela\s+white': 'Angela White',
        r'lana\s+rhoades': 'Lana Rhoades',
        r'mia\s+khalifa': 'Mia Khalifa',
        r'riley\s+reid': 'Riley Reid',
    }
    
    title_lower = title_clean.lower()
    
    for pattern, actress_name in known_patterns.items():
        if re.search(pattern, title_lower):
            return actress_name
    
    # Buscar nombres capitalizados (2-3 palabras)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    matches = re.findall(name_pattern, title_clean)
    
    generic_words = {'Video', 'Hot', 'Best', 'New', 'Top', 'Full', 'Hd', 
                    'Complete', 'Premium', 'Quality', 'Download', 'Watch',
                    'Porn', 'Xxx', 'Teen', 'Anal', 'Pov'}
    
    for match in matches:
        words = set(match.split())
        if not words & generic_words and len(match.split()) >= 2:
            return normalize_uploader_name(match)
    
    return None

def scrape_xgroovy_uploader(url):
    """
    Hace scraping de la página de XGroovy para obtener el uploader
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar uploader en XGroovy
        # Intentar varios selectores comunes
        selectors = [
            'a.model-link',
            'a.pornstar-link', 
            'div.uploader-name',
            'span.model-name',
            'a[href*="/pornstar/"]',
            'a[href*="/model/"]',
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                uploader = element.get_text().strip()
                if uploader and uploader != 'Unknown':
                    return normalize_uploader_name(uploader)
        
        # Buscar en el HTML de forma más genérica
        html_text = response.text.lower()
        
        # Patrón para extraer de meta tags
        meta_author = soup.find('meta', {'name': 'author'})
        if meta_author and meta_author.get('content'):
            return normalize_uploader_name(meta_author['content'])
        
        return None
        
    except Exception as e:
        return None

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "final_reorganize_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("REORGANIZACION DEFINITIVA - TITULO + SCRAPING")
log("="*70)

log("\n[1/5] Cargando historial...")
with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

unknown_entries = [e for e in history if e.get('uploader', '').lower() in ['unknown', 'na']]
log(f"      Total Unknown: {len(unknown_entries)}")

log("\n[2/5] Analizando titulos (metodo mejorado)...")

from_title = []
for entry in unknown_entries:
    title = entry.get('title', '')
    actress = extract_actress_from_title_enhanced(title)
    
    if actress and actress != 'Unknown':
        from_title.append({
            'entry': entry,
            'actress': actress,
            'method': 'Titulo',
            'title': title[:50]
        })

log(f"      Detectados del titulo: {len(from_title)}")

log("\n[3/5] Haciendo scraping de URLs para los restantes...")
log("      (Esto puede tardar varios minutos...)")

from_scraping = []
remaining = [e for e in unknown_entries if e not in [x['entry'] for x in from_title]]

for i, entry in enumerate(remaining, 1):
    url = entry.get('original_url', '') or entry.get('url', '')
    title = entry.get('title', '')[:50]
    
    if not url:
        continue
    
    log(f"  [{i}/{len(remaining)}] Scraping: {title}...")
    
    actress = scrape_xgroovy_uploader(url)
    
    if actress and actress != 'Unknown':
        from_scraping.append({
            'entry': entry,
            'actress': actress,
            'method': 'Scraping',
            'title': title
        })
        log(f"      Detectado: {actress}")
    else:
        log(f"      No detectado")
    
    # Esperar un poco para no sobrecargar el servidor
    time.sleep(0.5)

log(f"\n      Detectados por scraping: {len(from_scraping)}")

all_updates = from_title + from_scraping

log(f"\n[4/5] Total reorganizables: {len(all_updates)}")

if not all_updates:
    log("\nNo se pudo detectar ninguna actriz")
else:
    # Agrupar por actriz
    by_actress = {}
    for update in all_updates:
        actress = update['actress']
        if actress not in by_actress:
            by_actress[actress] = []
        by_actress[actress].append(update)
    
    log(f"\nActrices identificadas: {len(by_actress)}")
    log("-"*70)
    
    for actress, items in sorted(by_actress.items()):
        methods = set(item['method'] for item in items)
        log(f"\n  {actress} ({len(items)} archivos) - {', '.join(methods)}")
        for item in items[:2]:
            log(f"    - {item['title']}")
        if len(items) > 2:
            log(f"    ... y {len(items) - 2} mas")
    
    log("\n[5/5] Reorganizando archivos...")
    
    success_count = 0
    error_count = 0
    created_folders = set()
    
    for update in all_updates:
        entry = update['entry']
        actress = update['actress']
        file_path = Path(entry.get('file_path', '')) if entry.get('file_path') else None
        
        # Actualizar historial
        entry['uploader'] = actress
        
        # Mover archivo si existe
        if file_path and file_path.exists():
            actress_folder = TEMP_DOWNLOADS / actress
            actress_folder.mkdir(exist_ok=True)
            created_folders.add(actress)
            
            new_path = actress_folder / file_path.name
            
            # Manejar duplicados
            if new_path.exists():
                stem = new_path.stem
                suffix = new_path.suffix
                counter = 1
                while new_path.exists():
                    new_path = actress_folder / f"{stem}_{counter}{suffix}"
                    counter += 1
            
            try:
                shutil.move(str(file_path), str(new_path))
                entry['file_path'] = str(new_path)
                log(f"  OK: {file_path.name[:40]} -> {actress}/")
                success_count += 1
            except Exception as e:
                log(f"  ERROR: {file_path.name[:30]}: {str(e)[:20]}")
                error_count += 1
    
    # Guardar historial
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    # Los que quedan sin clasificar
    unclassified = len(unknown_entries) - len(all_updates)
    
    log("\n" + "="*70)
    log("RESUMEN FINAL")
    log("="*70)
    log(f"Total Unknown procesados: {len(unknown_entries)}")
    log(f"Detectados del titulo: {len(from_title)}")
    log(f"Detectados por scraping: {len(from_scraping)}")
    log(f"Actrices diferentes: {len(by_actress)}")
    log(f"Archivos movidos: {success_count}")
    log(f"Errores: {error_count}")
    log(f"Sin clasificar: {unclassified}")
    
    if created_folders:
        log("\nNuevas carpetas de actrices:")
        for actress in sorted(created_folders):
            count = len([u for u in all_updates if u['actress'] == actress])
            log(f"  - {actress} ({count} videos)")
    
    if success_count > 0:
        log("\nEXITO: Reorganizacion completada")
        log("  -> Recarga la pagina web (F5)")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE EN:\n{REPORT_FILE}\n")
