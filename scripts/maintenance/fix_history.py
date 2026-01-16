"""
Script simple para corregir historial - cambiar Unknown por Uncategorized
"""

import json
from pathlib import Path

HISTORY_FILE = Path("history.json")

print("Corrigiendo historial...")

with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

updated = 0
for entry in history:
    if entry.get('uploader') == 'Unknown':
        entry['uploader'] = 'Uncategorized'
        updated += 1
    
    # También actualizar rutas de archivos
    if 'file_path' in entry and '\\Unknown\\' in entry['file_path']:
        entry['file_path'] = entry['file_path'].replace('\\Unknown\\', '\\Uncategorized\\')

with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=2, ensure_ascii=False)

print(f"Actualizadas {updated} entradas")
print("Listo!")
