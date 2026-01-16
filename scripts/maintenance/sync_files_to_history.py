"""
Script mejorado para sincronizar archivos con metadata completa
Extrae duración y genera miniaturas usando FFmpeg
"""

import json
import os
import subprocess
from pathlib import Path
import datetime

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
THUMBNAILS_DIR = BASE_DIR / "static" / "thumbnails"

THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG_PATH = r'C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe'
FFPROBE_PATH = r'C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe'

def get_video_duration(video_path):
    """Obtiene la duración del video usando ffprobe"""
    try:
        cmd = [
            FFPROBE_PATH,
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return int(float(result.stdout.strip()))
        return 0
    except:
        return 0

def generate_thumbnail(video_path, output_path):
    """Genera miniatura del video"""
    try:
        cmd = [
            FFMPEG_PATH,
            '-i', str(video_path),
            '-ss', '00:00:05',  # Tomar frame en segundo 5
            '-vframes', '1',
            '-vf', 'scale=320:-1',
            '-y',
            str(output_path)
        ]
        subprocess.run(cmd, capture_output=True, timeout=15)
        return output_path.exists()
    except:
        return False

print("="*70)
print("SINCRONIZACION CON METADATA COMPLETA")
print("="*70)

# Cargar historial
with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
    history = json.load(f)

print(f"\nEntradas en historial: {len(history)}")

# Encontrar entradas sin metadata
entries_to_update = []
for entry in history:
    file_path = entry.get('file_path')
    if file_path and Path(file_path).exists():
        # Si no tiene thumbnail o duration es 0
        if not entry.get('thumbnail') or entry.get('duration', 0) == 0:
            entries_to_update.append(entry)

print(f"Entradas sin metadata completa: {len(entries_to_update)}")

if entries_to_update:
    print("\nExtrayendo metadata...")
    updated = 0
    
    for i, entry in enumerate(entries_to_update, 1):
        file_path = Path(entry['file_path'])
        print(f"  [{i}/{len(entries_to_update)}] {file_path.name[:40]}...", end=' ')
        
        # Extraer duración
        duration = get_video_duration(file_path)
        entry['duration'] = duration
        
        # Generar miniatura
        thumb_filename = f"{entry.get('download_id', file_path.stem)}.jpg"
        thumb_path = THUMBNAILS_DIR / thumb_filename
        
        if generate_thumbnail(file_path, thumb_path):
            entry['thumbnail'] = f"/static/thumbnails/{thumb_filename}"
            print(f"✓ ({duration}s)")
        else:
            entry['thumbnail'] = 'https://via.placeholder.com/320x180?text=Video'
            print(f"✓ (thumbnail fallback)")
        
        updated += 1
    
    # Guardar
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ {updated} entradas actualizadas con metadata")
else:
    print("\n✓ Todas las entradas ya tienen metadata")

print("\n" + "="*70)
print("COMPLETADO")
print("="*70)
