"""
Script para reorganizar archivos de la carpeta Unknown/Desconocido
Analiza títulos para extraer nombres de actrices y mover archivos a las carpetas correctas
"""

import os
import re
import json
import shutil
from pathlib import Path

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
    """
    Intenta extraer el nombre de la actriz del título del video
    """
    if not title:
        return None
    
    # Lista de nombres comunes de actrices para ayudar en la detección
    common_actress_names = [
        'sia', 'siberia', 'angela', 'white', 'mia', 'khalifa', 'riley', 'reid',
        'abella', 'danger', 'lana', 'rhoades', 'kendra', 'lust', 'alexis', 'texas',
        'brandi', 'love', 'nicole', 'aniston', 'lisa', 'ann', 'anna', 'polina',
        'emma', 'starr', 'megan', 'rain', 'dani', 'daniels', 'jenna', 'jameson',
        'madison', 'ivy', 'adriana', 'chechik', 'ava', 'addams', 'luna', 'star',
        'elsa', 'jean', 'karneli', 'bandi', 'lexi', 'lore', 'molly', 'redwolf',
        'julie', 'jess', 'miss', 'moons'
    ]
    
    title_lower = title.lower()
    
    # Método 1: Buscar patrones de nombres capitalizados (2-3 palabras)
    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'
    matches = re.findall(name_pattern, title)
    
    for match in matches:
        # Verificar si contiene algún nombre conocido
        match_lower = match.lower()
        if any(name in match_lower for name in common_actress_names):
            words = match.split()
            # Evitar palabras genéricas
            generic_words = ['Video', 'Hot', 'Best', 'New', 'Top', 'Full', 'Hd', 
                           'Complete', 'Premium', 'Quality', 'Online', 'Free']
            if not any(word in words for word in generic_words):
                return normalize_uploader_name(match)
    
    # Método 2: Buscar nombres en minúsculas (formato: nombre apellido)
    lowercase_pattern = r'\b([a-z]{3,12}\s+[a-z]{3,12})\b'
    matches = re.findall(lowercase_pattern, title_lower)
    
    for match in matches:
        if any(name in match for name in common_actress_names):
            # Capitalizar
            return normalize_uploader_name(match)
    
    # Método 3: Buscar nombres específicos conocidos
    known_patterns = [
        r'sia\s+siberia',
        r'karneli\s+bandi',
        r'lexi\s+lore',
        r'molly\s+red\s*wolf',
        r'julie\s+jess',
        r'angela\s+white',
    ]
    
    for pattern in known_patterns:
        match = re.search(pattern, title_lower)
        if match:
            return normalize_uploader_name(match.group(0))
    
    return None

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "reorganize_unknown_report.txt"

# Posibles nombres de la carpeta Unknown
UNKNOWN_FOLDERS = ['Unknown', 'Desconocido', 'NA', 'Na']

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

log("="*70)
log("REORGANIZADOR DE CARPETA DESCONOCIDO/UNKNOWN")
log("="*70)

log("\n[1/4] Buscando carpeta Unknown/Desconocido...")

unknown_folder = None
for folder_name in UNKNOWN_FOLDERS:
    folder_path = TEMP_DOWNLOADS / folder_name
    if folder_path.exists():
        unknown_folder = folder_path
        log(f"      Encontrada: {folder_name}")
        break

if not unknown_folder:
    log("\nOK: No se encontro carpeta Unknown/Desconocido")
    log(f"Reporte: {REPORT_FILE}")
    print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
    exit(0)

log("\n[2/4] Analizando archivos...")

files = list(unknown_folder.rglob('*'))
files = [f for f in files if f.is_file()]

log(f"      Total archivos: {len(files)}")

# Analizar cada archivo
moves = []
for file_path in files:
    # Intentar extraer actriz del nombre del archivo
    actress = extract_actress_from_title(file_path.stem)
    
    if actress and actress != 'Unknown':
        moves.append((file_path, actress))

log(f"\n[3/4] Archivos identificables: {len(moves)}")

if not moves:
    log("\nNo se pudieron identificar actrices en los titulos")
    log("Los archivos permaneceran en la carpeta Unknown")
else:
    log("\nArchivos a reorganizar:")
    log("-"*70)
    
    # Agrupar por actriz
    by_actress = {}
    for file_path, actress in moves:
        if actress not in by_actress:
            by_actress[actress] = []
        by_actress[actress].append(file_path)
    
    for actress, file_list in sorted(by_actress.items()):
        log(f"\n  {actress} ({len(file_list)} archivos)")
        for f in file_list[:3]:  # Mostrar primeros 3
            log(f"    - {f.name}")
        if len(file_list) > 3:
            log(f"    ... y {len(file_list) - 3} mas")
    
    log("\n[4/4] Moviendo archivos...")
    
    history = load_history()
    success_count = 0
    error_count = 0
    
    for file_path, actress in moves:
        # Crear carpeta de actriz si no existe
        actress_folder = TEMP_DOWNLOADS / actress
        actress_folder.mkdir(exist_ok=True)
        
        # Nueva ruta del archivo
        new_path = actress_folder / file_path.name
        
        # Si existe, agregar sufijo
        if new_path.exists():
            stem = new_path.stem
            suffix = new_path.suffix
            counter = 1
            while new_path.exists():
                new_path = actress_folder / f"{stem}_{counter}{suffix}"
                counter += 1
        
        try:
            # Mover archivo
            shutil.move(str(file_path), str(new_path))
            log(f"  OK: {file_path.name} -> {actress}/")
            success_count += 1
            
            # Actualizar historial
            old_path_str = str(file_path).replace('/', '\\')
            new_path_str = str(new_path).replace('/', '\\')
            
            for entry in history:
                if 'file_path' in entry and entry['file_path'] == old_path_str:
                    entry['file_path'] = new_path_str
                    entry['uploader'] = actress
                    break
        
        except Exception as e:
            log(f"  ERROR: {file_path.name}: {e}")
            error_count += 1
    
    # Guardar historial actualizado
    if success_count > 0:
        save_history(history)
        log(f"\n  Historial actualizado: {success_count} rutas")
    
    log("\n" + "="*70)
    log("RESUMEN")
    log("="*70)
    log(f"Archivos analizados: {len(files)}")
    log(f"Actrices identificadas: {len(by_actress)}")
    log(f"Archivos movidos: {success_count}")
    log(f"Errores: {error_count}")
    log(f"Permanecen en Unknown: {len(files) - success_count}")
    
    if success_count > 0:
        log("\nEXITO: Archivos reorganizados")
        log("  -> Recarga la pagina web para ver los cambios")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
