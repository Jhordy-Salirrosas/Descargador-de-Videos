"""
Reorganiza archivos de "XGroovy Videos" por nombre de actriz mediante scraping
"""

import json
import shutil
from pathlib import Path
import re
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

def scrape_xgroovy_uploader(url):
    """Hace scraping de XGroovy para obtener el uploader"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscar uploader en XGroovy - probar múltiples selectores
        # Método 1: Links a modelos/pornstars
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            if '/pornstar/' in href or '/model/' in href:
                uploader = link.get_text().strip()
                if uploader and len(uploader) > 2:
                    return normalize_uploader_name(uploader)
        
        # Método 2: Buscar en clases específicas
        possible_selectors = [
            'a.model-link',
            'a.pornstar-link',
            'div.model-name',
            'span.uploader',
        ]
        
        for selector in possible_selectors:
            element = soup.select_one(selector)
            if element:
                uploader = element.get_text().strip()
                if uploader:
                    return normalize_uploader_name(uploader)
        
        # Método 3: Buscar "Pornstar:" o "Model:" en el texto
        text = soup.get_text()
        patterns = [
            r'Pornstar[:\s]+([A-Za-z\s]+)',
            r'Model[:\s]+([A-Za-z\s]+)',
            r'Uploader[:\s]+([A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                uploader = match.group(1).strip()
                if uploader and len(uploader) > 2:
                    return normalize_uploader_name(uploader)
        
        return None
        
    except Exception as e:
        return None

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "xgroovy_reorganize_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("REORGANIZACION DE XGROOVY VIDEOS POR ACTRIZ - SCRAPING")
log("="*70)

log("\n[1/4] Cargando historial...")
with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

# Buscar entradas de XGroovy Videos
xgroovy_entries = [e for e in history if e.get('uploader', '') == 'XGroovy Videos']
log(f"      Archivos en XGroovy Videos: {len(xgroovy_entries)}")

if not xgroovy_entries:
    log("\nNo hay archivos en carpeta 'XGroovy Videos'")
    print(f"\nREPORTE EN:\n{REPORT_FILE}\n")
    exit(0)

log("\n[2/4] Haciendo scraping de URLs...")
log("      NOTA: Esto tardara varios minutos (~90 paginas)")
log("      Para evitar ban, hay pausa de 1seg entre requests\n")

detected = []
failed = []

for i, entry in enumerate(xgroovy_entries, 1):
    url = entry.get('original_url', '') or entry.get('url', '')
    title = entry.get('title', '')[:50]
    
    if not url:
        log(f"  [{i}/{len(xgroovy_entries)}] Sin URL: {title}")
        failed.append(entry)
        continue
    
    log(f"  [{i}/{len(xgroovy_entries)}] Scraping: {title[:40]}...")
    
    actress = scrape_xgroovy_uploader(url)
    
    if actress and actress != 'Unknown':
        detected.append({
            'entry': entry,
            'actress': actress,
            'title': title,
            'file_path': entry.get('file_path', '')
        })
        log(f"      ✓ Detectado: {actress}")
    else:
        failed.append(entry)
        log(f"      ✗ No detectado")
    
    # Pausa para no sobrecargar servidor
    time.sleep(1)

log(f"\n      Exitosos: {len(detected)}")
log(f"      Fallidos: {len(failed)}")

if not detected:
    log("\nNo se pudo detectar ninguna actriz mediante scraping")
else:
    # Agrupar por actriz
    by_actress = {}
    for item in detected:
        actress = item['actress']
        if actress not in by_actress:
            by_actress[actress] = []
        by_actress[actress].append(item)
    
    log(f"\n[3/4] Actrices identificadas: {len(by_actress)}")
    log("-"*70)
    
    for actress, items in sorted(by_actress.items()):
        log(f"\n  {actress} ({len(items)} archivos)")
        for item in items[:2]:
            log(f"    - {item['title']}")
        if len(items) > 2:
            log(f"    ... y {len(items) - 2} mas")
    
    log("\n[4/4] Reorganizando archivos...")
    
    success_count = 0
    error_count = 0
    created_folders = set()
    
    for item in detected:
        entry = item['entry']
        actress = item['actress']
        file_path = Path(item['file_path']) if item['file_path'] else None
        
        # Actualizar historial
        entry['uploader'] = actress
        
        # Mover archivo
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
    
    log("\n" + "="*70)
    log("RESUMEN")
    log("="*70)
    log(f"Total procesados: {len(xgroovy_entries)}")
    log(f"Actrices detectadas: {len(by_actress)}")
    log(f"Archivos reorganizados: {success_count}")
    log(f"Errores: {error_count}")
    log(f"Permanecen en XGroovy Videos: {len(failed)}")
    
    if created_folders:
        log("\nNuevas carpetas de actrices creadas:")
        for actress in sorted(created_folders):
            count = len([d for d in detected if d['actress'] == actress])
            log(f"  - {actress} ({count} videos)")
    
    if success_count > 0:
        log("\nEXITO: Reorganizacion completada")
        log("  -> Recarga la pagina web (F5)")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE EN:\n{REPORT_FILE}\n")
