"""
Script para diagnosticar videos faltantes
"""

import json
from pathlib import Path

HISTORY_FILE = Path("history.json")
TEMP_DOWNLOADS = Path("temp_downloads")

print("="*70)
print("DIAGNOSTICO DE VIDEOS FALTANTES")
print("="*70)

with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

print(f"\nTotal entradas en historial: {len(history)}")

# Agrupar por estado
by_status = {}
for entry in history:
    status = entry.get('status', 'unknown')
    by_status[status] = by_status.get(status, 0) + 1

print("\nPor estado:")
for status, count in sorted(by_status.items()):
    print(f"  {status}: {count}")

# Verificar cuántos tienen archivos missing
print("\nVerificando archivos físicos...")

existing = 0
missing = 0
no_path = 0

missing_list = []

for entry in history:
    file_path = entry.get('file_path', '')
    
    if not file_path:
        no_path += 1
        continue
    
    path = Path(file_path)
    if path.exists():
        existing += 1
    else:
        missing += 1
        missing_list.append({
            'title': entry.get('title', 'Sin título')[:50],
            'status': entry.get('status', 'unknown'),
            'uploader': entry.get('uploader', 'Unknown'),
            'path': str(path)
        })

print(f"\n  Archivos existentes: {existing}")
print(f"  Archivos faltantes: {missing}")
print(f"  Sin ruta: {no_path}")

if missing > 0:
    print(f"\nMuestra de archivos faltantes (primeros 10):")
    for i, item in enumerate(missing_list[:10], 1):
        print(f"\n  {i}. {item['title']}")
        print(f"     Estado: {item['status']}")
        print(f"     Uploader: {item['uploader']}")
        print(f"     Ruta: ...{item['path'][-60:]}")

# Agrupar faltantes por uploader
if missing > 0:
    by_uploader = {}
    for item in missing_list:
        uploader = item['uploader']
        by_uploader[uploader] = by_uploader.get(uploader, 0) + 1
    
    print(f"\nFaltantes por uploader:")
    for uploader, count in sorted(by_uploader.items(), key=lambda x: -x[1]):
        print(f"  {uploader}: {count}")

print("\n" + "="*70)
