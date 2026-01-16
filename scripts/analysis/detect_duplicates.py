"""
Script para detectar carpetas duplicadas - guarda resultado en archivo
"""

import os
import shutil
from pathlib import Path
import json

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
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
REPORT_FILE = BASE_DIR / "temp" / "output" / "duplicate_folders_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def write_log(msg):
    """Escribe en archivo y consola"""
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

def find_duplicate_folders():
    """Detecta carpetas duplicadas"""
    if not TEMP_DOWNLOADS.exists():
        return {}
    
    folders = [f for f in TEMP_DOWNLOADS.iterdir() if f.is_dir()]
    
    grouped = {}
    for folder in folders:
        normalized = normalize_uploader_name(folder.name)
        if normalized not in grouped:
            grouped[normalized] = []
        grouped[normalized].append(folder)
    
    duplicates = {k: v for k, v in grouped.items() if len(v) > 1}
    
    return duplicates, grouped

def count_files(folder):
    """Cuenta archivos en una carpeta"""
    return sum(1 for _ in folder.rglob('*') if _.is_file())

write_log("="*70)
write_log("DETECTOR DE CARPETAS DUPLICADAS")
write_log("="*70)

write_log("\n[1/2] Escaneando carpetas...")
duplicates, all_folders = find_duplicate_folders()

total_folders = len([f for folders in all_folders.values() for f in folders])
write_log(f"Total de carpetas encontradas: {total_folders}")

if not duplicates:
    write_log("\nRESULTADO: No se encontraron carpetas duplicadas")
    write_log("Todas las carpetas tienen nombres unicos despues de normalizacion.")
else:
    write_log(f"\nRESULTADO: Encontrados {len(duplicates)} grupos duplicados")
    write_log("="*70)
    
    for normalized_name, folder_list in duplicates.items():
        write_log(f"\nGRUPO: {normalized_name}")
        write_log("-"*70)
        
        total_files = 0
        for i, folder in enumerate(folder_list, 1):
            file_count = count_files(folder)
            total_files += file_count
            write_log(f"  [{i}] Carpeta: {folder.name}")
            write_log(f"      Archivos: {file_count}")
        
        write_log(f"\n  Total archivos en grupo: {total_files}")
        write_log(f"  Se fusionarian en: {normalized_name}")

write_log("\n" + "="*70)
write_log("RESUMEN")
write_log("="*70)
write_log(f"Total carpetas: {total_folders}")
write_log(f"Grupos unicos: {len(all_folders)}")
write_log(f"Grupos duplicados: {len(duplicates)}")

if duplicates:
    total_to_merge = sum(len(v) - 1 for v in duplicates.values())
    write_log(f"Carpetas a fusionar: {total_to_merge}")
    write_log("\nPara fusionar, ejecutar:")
    write_log("  python merge_duplicate_folders.py")
    write_log("  y confirmar con 'SI'")

write_log("\n" + "="*70)
write_log(f"Reporte guardado en: {REPORT_FILE}")

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
