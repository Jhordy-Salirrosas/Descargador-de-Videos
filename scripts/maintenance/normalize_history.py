"""
Script para normalizar nombres de uploaders en history.json - version con output a archivo
"""

import json
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

BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "history.json"
BACKUP_FILE = BASE_DIR / "temp" / "output" / "history_backup.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "normalize_report.txt"

BACKUP_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("NORMALIZADOR DE NOMBRES EN HISTORIAL")
log("="*70)

log("\n[1/4] Cargando historial...")
with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

log(f"      Total entradas: {len(history)}")

log("\n[2/4] Creando backup...")
with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=2, ensure_ascii=False)
log(f"      Backup: {BACKUP_FILE}")

log("\n[3/4] Normalizando nombres de uploaders...")

changes = {}
for entry in history:
    if 'uploader' in entry:
        original = entry['uploader']
        normalized = normalize_uploader_name(original)
        
        if original != normalized:
            entry['uploader'] = normalized
            
            if original not in changes:
                changes[original] = {'normalized': normalized, 'count': 0}
            changes[original]['count'] += 1

log(f"\n      Cambios realizados:")
if changes:
    for original, info in sorted(changes.items()):
        log(f"      - '{original}' -> '{info['normalized']}' ({info['count']} entradas)")
else:
    log("      - No se encontraron cambios necesarios")

log("\n[4/4] Guardando historial actualizado...")
with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=2, ensure_ascii=False)

log("\n" + "="*70)
log("RESUMEN")
log("="*70)
log(f"Total entradas: {len(history)}")
log(f"Uploaders normalizados: {len(changes)}")
log(f"Total cambios: {sum(c['count'] for c in changes.values())}")

if changes:
    log("\nEXITO: Historial actualizado")
    log("  -> Recarga la pagina web para ver los cambios")
else:
    log("\nOK: No se requirieron cambios")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
