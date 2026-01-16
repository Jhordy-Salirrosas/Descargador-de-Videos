"""
Script DEFINITIVO de limpieza - Organiza TODO el proyecto
"""

import os
import shutil
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"

print("="*70)
print("LIMPIEZA DEFINITIVA DEL PROYECTO")
print("="*70)

# 1. Mover archivos sueltos de temp_downloads a carpeta Unknown
print("\n[1/3] Moviendo archivos sueltos a carpeta Unknown...")

video_extensions = {'.mp4', '.mkv', '.webm', '.avi', '.mov'}
loose_files = [f for f in TEMP_DOWNLOADS.iterdir() if f.is_file() and f.suffix.lower() in video_extensions]

print(f"  Archivos sueltos encontrados: {len(loose_files)}")

if loose_files:
    unknown_folder = TEMP_DOWNLOADS / "Unknown"
    unknown_folder.mkdir(exist_ok=True)
    
    moved = 0
    for video_file in loose_files:
        try:
            dest = unknown_folder / video_file.name
            counter = 1
            while dest.exists():
                stem = dest.stem
                suffix = dest.suffix
                dest = unknown_folder / f"{stem}_{counter}{suffix}"
                counter += 1
            
            shutil.move(str(video_file), str(dest))
            print(f"  Movido: {video_file.name}")
            moved += 1
        except Exception as e:
            print(f"  ERROR: {video_file.name}: {e}")
    
    print(f"  Total movidos: {moved}")

# 2. Renombrar carpetas problemáticas
print("\n[2/3] Renombrando carpetas...")

# Renombrar Unknown a Uncategorized si existe
unknown_path = TEMP_DOWNLOADS / "Unknown"
uncategorized_path = TEMP_DOWNLOADS / "Uncategorized"

if unknown_path.exists():
    if uncategorized_path.exists():
        # Fusionar
        print("  Fusionando Unknown con Uncategorized...")
        for file in unknown_path.rglob('*'):
            if file.is_file():
                rel = file.relative_to(unknown_path)
                dest = uncategorized_path / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                counter = 1
                while dest.exists():
                    dest = dest.parent / f"{file.stem}_{counter}{file.suffix}"
                    counter += 1
                shutil.move(str(file), str(dest))
        shutil.rmtree(unknown_path)
        print("  Unknown fusionada y eliminada")
    else:
        unknown_path.rename(uncategorized_path)
        print("  Unknown → Uncategorized")

# Renombrar XGroovy Videos a XGroovy
xgroovy_videos = TEMP_DOWNLOADS / "XGroovy Videos"
xgroovy = TEMP_DOWNLOADS / "XGroovy"

if xgroovy_videos.exists():
    if xgroovy.exists():
        # Fusionar
        print("  Fusionando XGroovy Videos con XGroovy...")
        for file in xgroovy_videos.rglob('*'):
            if file.is_file():
                rel = file.relative_to(xgroovy_videos)
                dest = xgroovy / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                counter = 1
                while dest.exists():
                    dest = dest.parent / f"{file.stem}_{counter}{file.suffix}"
                    counter += 1
                shutil.move(str(file), str(dest))
        shutil.rmtree(xgroovy_videos)
        print("  XGroovy Videos fusionada y eliminada")
    else:
        xgroovy_videos.rename(xgroovy)
        print("  XGroovy Videos → XGroovy")

# 3. Actualizar historial
print("\n[3/3] Actualizando historial...")

with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

updated = 0
for entry in history:
    original_uploader = entry.get('uploader')
    
    # Cambiar Unknown y XGroovy Videos
    if original_uploader == 'Unknown':
        entry['uploader'] = 'Uncategorized'
        updated += 1
    elif original_uploader == 'XGroovy Videos':
        entry['uploader'] = 'XGroovy'
        updated += 1
    
    # Actualizar rutas de archivos
    if 'file_path' in entry:
        path = entry['file_path']
        path = path.replace('\\Unknown\\', '\\Uncategorized\\')
        path = path.replace('\\XGroovy Videos\\', '\\XGroovy\\')
        entry['file_path'] = path

with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=2, ensure_ascii=False)

print(f"  Entradas actualizadas: {updated}")

print("\n" + "="*70)
print("LIMPIEZA COMPLETADA")
print("="*70)
print("\nPasos siguientes:")
print("  1. Reinicia el servidor (Ctrl+C y luego 'python app.py')")
print("  2. Recarga la pagina web con Ctrl+Shift+R")
print("="*70)
