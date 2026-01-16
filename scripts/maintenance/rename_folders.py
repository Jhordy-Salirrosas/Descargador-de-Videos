"""
Script para renombrar carpetas de uploaders para que coincidan con nombres normalizados
"""

import os
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

BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
REPORT_FILE = BASE_DIR / "temp" / "output" / "folder_rename_report.txt"

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
if REPORT_FILE.exists():
    REPORT_FILE.unlink()

def log(msg):
    print(msg)
    with open(REPORT_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')

log("="*70)
log("RENOMBRADOR DE CARPETAS DE UPLOADERS")
log("="*70)

log("\n[1/2] Escaneando carpetas...")

folders = [f for f in TEMP_DOWNLOADS.iterdir() if f.is_dir()]
log(f"      Total carpetas: {len(folders)}")

renames = []
for folder in folders:
    normalized = normalize_uploader_name(folder.name)
    
    if folder.name != normalized:
        renames.append((folder, normalized))

log(f"\n[2/2] Carpetas a renombrar: {len(renames)}")

if not renames:
    log("\nOK: Todas las carpetas ya tienen nombres normalizados")
else:
    log("\nCarpetas que seran renombradas:")
    log("-"*70)
    
    for folder, new_name in renames:
        file_count = sum(1 for _ in folder.rglob('*') if _.is_file())
        log(f"\n  '{folder.name}'")
        log(f"      -> '{new_name}'")
        log(f"      Archivos: {file_count}")
    
    log("\n" + "="*70)
    log("Procediendo con renombrado...")
    
    success_count = 0
    error_count = 0
    
    for folder, new_name in renames:
        new_path = folder.parent / new_name
        
        # Si la carpeta destino ya existe, fusionar
        if new_path.exists():
            log(f"\n  Fusionando '{folder.name}' en '{new_name}' (ya existe)...")
            
            # Mover todos los archivos
            for file_path in folder.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(folder)
                    target = new_path / rel_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Si existe, agregar sufijo
                    if target.exists():
                        stem = target.stem
                        suffix = target.suffix
                        counter = 1
                        while target.exists():
                            target = target.parent / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    shutil.move(str(file_path), str(target))
            
            # Eliminar carpeta original
            try:
                shutil.rmtree(folder)
                log(f"  OK: Fusionado y eliminado '{folder.name}'")
                success_count += 1
            except Exception as e:
                log(f"  ERROR: No se pudo eliminar '{folder.name}': {e}")
                error_count += 1
        else:
            # Renombrar directamente
            try:
                folder.rename(new_path)
                log(f"  OK: Renombrado '{folder.name}' -> '{new_name}'")
                success_count += 1
            except Exception as e:
                log(f"  ERROR: No se pudo renombrar '{folder.name}': {e}")
                error_count += 1

    log("\n" + "="*70)
    log("RESUMEN")
    log("="*70)
    log(f"Carpetas procesadas: {len(renames)}")
    log(f"Exito: {success_count}")
    log(f"Errores: {error_count}")
    
    if success_count > 0:
        log("\nEXITO: Carpetas renombradas")
        log("  -> Recarga la pagina web para ver los cambios")

log(f"\nReporte: {REPORT_FILE}")
log("="*70)

print(f"\nREPORTE GUARDADO EN:\n{REPORT_FILE}\n")
