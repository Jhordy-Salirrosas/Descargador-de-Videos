"""
Script completo de reorganización - Analiza historial y reorganiza archivos Unknown/NA
"""

import json
import shutil
from pathlib import Path
import re

def normalize_uploader_name(uploader):
    """Normaliza el nombre del uploader"""
    if not uploader or uploader == 'Unknown':
        return 'Unknown'
    
    name = uploader.replace('_', ' ')
    name = "".join([c for c in name if c.isalnum() or c in (' ', '-')]).strip()
    name = ' '.join(word.capitalize() for word in name.split())
    
    if not name:
        return 'Unknown'
    
    return name

def extract_actress_from_title(title):
    """Extrae nombre de actriz del título"""
    if not title:
        return None
    
    # Nombres conocidos de actrices
    known_actresses = {
        # Usar patrones para detectar nombres
        r'sia\s+siberia': 'Sia Siberia',
        r'karneli\s+bandi': 'Karneli Bandi',
        r'lexi\s+lore': 'Lexi Lore',
        r'molly\s*red\s*wolf': 'Molly Redwolf',
        r'julie\s+jess': 'Julie Jess',
        r'angela\s+white': 'Angela White',
        r'mia\s+khalifa': 'Mia Khalifa',
        r'riley\s+reid': 'Riley Reid',
        r'lana\s+rhoades': 'Lana Rhoades',
        r'miss\s+moons': 'Miss Moons',
    }
    
    title_lower = title.lower()
    
    # Buscar nombres conocidos
    for pattern, actress_name in known_actresses.items():
        if re.search(pattern, title_lower):
            return actress_name
    
    # Buscar patrones de nombres capitalizados
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    matches = re.findall(name_pattern, title)
    
    if matches:
        # Evitar palabras genéricas
        generic_words = ['Video', 'Hot', 'Best', 'New', 'Top', 'Full', 'Hd', 
                        'Complete', 'Premium', 'Quality', 'Online', 'Free', 
                        'Download', 'Watch', 'Porn', 'Xxx']
        
        for match in matches:
            words = match.split()
            if len(words) >= 2 and not any(word in generic_words for word in words):
                return normalize_uploader_name(match)
    
    return None

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "full_reorganize_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("REORGANIZACION COMPLETA - HISTORIAL + ARCHIVOS")
log("="*70)

log("\n[1/3] Cargando historial...")
with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

# Filtrar entradas con uploader Unknown/NA
unknown_entries = [e for e in history if e.get('uploader', '').lower() in ['unknown', 'na', 'desconocido']]

log(f"      Total entradas en historial: {len(history)}")
log(f"      Entradas con Unknown/NA: {len(unknown_entries)}")

log("\n[2/3] Analizando titulos y extrayendo actrices...")

updates = []
for entry in unknown_entries:
    title = entry.get('title', '')
    file_path = entry.get('file_path', '')
    
    # Intentar extraer actriz
    actress = extract_actress_from_title(title)
    
    if actress and actress != 'Unknown':
        updates.append({
            'entry': entry,
            'old_uploader': entry.get('uploader', 'Unknown'),
            'new_uploader': actress,
            'title': title[:60],
            'file_path': file_path
        })

log(f"      Actrices identificadas: {len(updates)} de {len(unknown_entries)}")

if not updates:
    log("\nNo se encontraron archivos reorganizables")
    log("Todos los archivos permanecen como Unknown")
else:
    # Agrupar por actriz
    by_actress = {}
    for update in updates:
        actress = update['new_uploader']
        if actress not in by_actress:
            by_actress[actress] = []
        by_actress[actress].append(update)
    
    log("\nArchivos a reorganizar por actriz:")
    log("-"*70)
    for actress, items in sorted(by_actress.items()):
        log(f"\n  {actress} ({len(items)} archivos)")
        for item in items[:3]:
            log(f"    - {item['title']}")
        if len(items) > 3:
            log(f"    ... y {len(items) - 3} mas")
    
    log("\n[3/3] Reorganizando archivos y actualizando historial...")
    
    success_count = 0
    error_count = 0
    history_updated = 0
    
    for update in updates:
        entry = update['entry']
        new_uploader = update['new_uploader']
        file_path = Path(update['file_path']) if update['file_path'] else None
        
        # Actualizar historial siempre
        entry['uploader'] = new_uploader
        history_updated += 1
        
        # Si el archivo existe, moverlo
        if file_path and file_path.exists():
            # Crear carpeta de actriz
            actress_folder = TEMP_DOWNLOADS / new_uploader
            actress_folder.mkdir(exist_ok=True)
            
            # Nueva ruta
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
                log(f"  OK: {file_path.name[:50]} -> {new_uploader}/")
                success_count += 1
            except Exception as e:
                log(f"  ERROR: {file_path.name[:40]}: {str(e)[:30]}")
                error_count += 1
    
    # Guardar historial actualizado
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    log("\n" + "="*70)
    log("RESUMEN")
    log("="*70)
    log(f"Entradas Unknown/NA: {len(unknown_entries)}")
    log(f"Actrices identificadas: {len(by_actress)}")
    log(f"Historial actualizado: {history_updated} entradas")
    log(f"Archivos movidos: {success_count}")
    log(f"Errores: {error_count}")
    log(f"Permanecen Unknown: {len(unknown_entries) - len(updates)}")
    
    if success_count > 0 or history_updated > 0:
        log("\nEXITO: Reorganizacion completada")
        log("  -> Recarga la pagina web (F5) para ver los cambios")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
