"""
Script de análisis automático - Guarda resultados en archivo
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Rutas
BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"
REPORT_FILE = BASE_DIR / "temp" / "output" / "maintenance_report.txt"

# Asegurar que existe el directorio de output
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

def write_log(msg):
    """Escribe en archivo y consola"""
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

# Limpiar archivo anterior
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def load_history():
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def scan_downloaded_files():
    files = []
    if not TEMP_DOWNLOADS.exists():
        return files
    
    for file_path in TEMP_DOWNLOADS.rglob('*'):
        if file_path.is_file():
            files.append({
                'path': str(file_path),
                'name': file_path.name,
                'size': file_path.stat().st_size,
                'folder': file_path.parent.name
            })
    return files

def check_video_integrity(file_path):
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,duration',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(file_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10, encoding='utf-8', errors='ignore')
        
        if result.returncode != 0:
            return False, 0, "FFprobe error"
        
        try:
            data = json.loads(result.stdout)
            
            if 'streams' in data and len(data['streams']) > 0:
                codec = data['streams'][0].get('codec_name', '')
                duration = float(data.get('format', {}).get('duration', 0))
                
                if codec and duration > 0:
                    return True, duration, None
                elif duration == 0:
                    return False, 0, "Duration is 0"
                else:
                    return False, 0, "No codec"
            else:
                return False, 0, "No stream"
        except:
            return False, 0, "Parse error"
            
    except subprocess.TimeoutExpired:
        return False, 0, "Timeout"
    except FileNotFoundError:
        return False, 0, "FFprobe not found"
    except Exception as e:
        return False, 0, str(e)[:30]

write_log("=" * 70)
write_log(f"ANALISIS DE MANTENIMIENTO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
write_log("=" * 70)

write_log("\n[1/3] Escaneando archivos descargados...")
files = scan_downloaded_files()
write_log(f"      Encontrados: {len(files)} archivos")

write_log("\n[2/3] Cargando historial...")
history = load_history()
write_log(f"      Entradas: {len(history)}")

# Análisis de sincronización
file_paths = {os.path.normpath(f['path']): f for f in files}
history_paths = {}

for entry in history:
    if 'file_path' in entry and entry.get('status') == 'completed':
        normalized = os.path.normpath(entry['file_path'])
        history_paths[normalized] = entry

orphaned_files = [file_paths[p] for p in file_paths if p not in history_paths]
missing_files = [history_paths[p] for p in history_paths if p not in file_paths and not os.path.exists(p)]

write_log("\n" + "=" * 70)
write_log("RESULTADOS DE SINCRONIZACION")
write_log("=" * 70)
write_log(f"Archivos sincronizados: {len(file_paths) - len(orphaned_files)}")
write_log(f"Archivos sin historial: {len(orphaned_files)}")
write_log(f"Entradas sin archivo: {len(missing_files)}")

if orphaned_files:
    write_log(f"\nARCHIVOS SIN REGISTRO ({len(orphaned_files)}):")
    for f in orphaned_files[:10]:
        size_mb = f['size'] / (1024 * 1024)
        write_log(f"  - {f['folder']}/{f['name']} ({size_mb:.2f} MB)")
    if len(orphaned_files) > 10:
        write_log(f"  ... y {len(orphaned_files) - 10} mas")

if missing_files:
    write_log(f"\nENTRADAS SIN ARCHIVO ({len(missing_files)}):")
    for entry in missing_files[:10]:
        write_log(f"  - {entry.get('title', 'Unknown')[:60]}")
    if len(missing_files) > 10:
        write_log(f"  ... y {len(missing_files) - 10} mas")

# Verificación de integridad (muestra)
write_log("\n[3/3] Verificando integridad (muestra de 10 videos)...")

video_extensions = {'.mp4', '.mkv', '.webm', '.avi', '.mov'}
videos = [f for f in files if Path(f['path']).suffix.lower() in video_extensions]

write_log(f"      Videos totales: {len(videos)}")

corrupted = []
valid = []

for i, video in enumerate(videos[:10], 1):
    is_valid, duration, error = check_video_integrity(video['path'])
    
    if is_valid:
        valid.append(video)
        write_log(f"  [{i}/10] OK: {video['name'][:45]} ({duration:.1f}s)")
    else:
        corrupted.append({**video, 'error': error})
        write_log(f"  [{i}/10] CORRUPTO: {video['name'][:45]} - {error}")

write_log("\n" + "=" * 70)
write_log("RESUMEN FINAL")
write_log("=" * 70)
write_log(f"Total archivos: {len(files)}")
write_log(f"Total videos: {len(videos)}")
write_log(f"Sincronizados: {len(file_paths) - len(orphaned_files)}")
write_log(f"Huerfanos: {len(orphaned_files)}")
write_log(f"Sin archivo: {len(missing_files)}")
write_log(f"Videos OK (muestra): {len(valid)}")
write_log(f"Videos CORRUPTOS (muestra): {len(corrupted)}")

write_log("\nRECOMENDACIONES:")
if orphaned_files:
    write_log("  - Archivos sin historial detectados")
if missing_files:
    write_log("  - Ejecutar limpieza de historial (maintenance.py opcion 3)")
if corrupted:
    write_log("  - Videos corruptos detectados, ejecutar verificacion completa")
if not orphaned_files and not missing_files and not corrupted:
    write_log("  - Todo OK!")

write_log("\n" + "=" * 70)
write_log(f"Reporte guardado en: {REPORT_FILE}")

print(f"\n\nREPORTE COMPLETO GUARDADO EN:\n{REPORT_FILE}\n")
