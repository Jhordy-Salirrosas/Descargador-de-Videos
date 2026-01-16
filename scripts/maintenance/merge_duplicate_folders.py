"""
Script para fusionar carpetas duplicadas de uploaders en temp_downloads
Ejemplo: "Karneli_Bandi" y "Karneli Bandi" se fusionan en una sola carpeta
"""

import os
import shutil
from pathlib import Path
import json

# Importar función de normalización desde app.py
import sys
sys.path.insert(0, str(Path(__file__).parent))

def normalize_uploader_name(uploader):
    """
    Normaliza el nombre del uploader para evitar carpetas duplicadas.
    (Copia de la función en app.py)
    """
    if not uploader or uploader == 'Unknown':
        return 'Unknown'
    
    # Reemplazar guiones bajos con espacios
    name = uploader.replace('_', ' ')
    
    # Eliminar caracteres especiales, mantener solo alfanuméricos, espacios y guiones
    name = "".join([c for c in name if c.isalnum() or c in (' ', '-')]).strip()
    
    # Capitalizar cada palabra (Title Case)
    name = ' '.join(word.capitalize() for word in name.split())
    
    # Si después de limpiar está vacío, retornar Unknown
    if not name:
        return 'Unknown'
    
    return name

# Rutas
BASE_DIR = Path(__file__).parent
TEMP_DOWNLOADS = BASE_DIR / "temp_downloads"
HISTORY_FILE = BASE_DIR / "history.json"

def load_history():
    """Carga el archivo de historial"""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    """Guarda el historial"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def find_duplicate_folders():
    """
    Detecta carpetas duplicadas basándose en nombres normalizados
    Retorna: dict {nombre_normalizado: [lista_de_carpetas_originales]}
    """
    if not TEMP_DOWNLOADS.exists():
        return {}
    
    folders = [f for f in TEMP_DOWNLOADS.iterdir() if f.is_dir()]
    
    # Agrupar por nombre normalizado
    grouped = {}
    for folder in folders:
        normalized = normalize_uploader_name(folder.name)
        if normalized not in grouped:
            grouped[normalized] = []
        grouped[normalized].append(folder)
    
    # Filtrar solo los que tienen duplicados
    duplicates = {k: v for k, v in grouped.items() if len(v) > 1}
    
    return duplicates

def count_files(folder):
    """Cuenta archivos en una carpeta"""
    return sum(1 for _ in folder.rglob('*') if _.is_file())

def merge_folders(duplicates, dry_run=True):
    """
    Fusiona carpetas duplicadas
    - duplicates: dict de find_duplicate_folders()
    - dry_run: Si True, solo muestra qué haría sin hacer cambios
    """
    total_merged = 0
    total_moved = 0
    
    for normalized_name, folder_list in duplicates.items():
        print(f"\n{'='*70}")
        print(f"GRUPO: {normalized_name}")
        print(f"{'='*70}")
        
        # Mostrar todas las carpetas del grupo
        for i, folder in enumerate(folder_list, 1):
            file_count = count_files(folder)
            print(f"  [{i}] {folder.name}")
            print(f"      Archivos: {file_count}")
            print(f"      Ruta: {folder}")
        
        # Elegir carpeta destino (la primera que coincide con el nombre normalizado)
        # Si ninguna coincide exactamente, usar la que tiene más archivos
        target_folder = None
        for folder in folder_list:
            if folder.name == normalized_name:
                target_folder = folder
                break
        
        if not target_folder:
            # Usar la carpeta con más archivos como destino
            target_folder = max(folder_list, key=count_files)
        
        print(f"\n  → CARPETA DESTINO: {target_folder.name}")
        
        # Mover archivos de las otras carpetas
        for folder in folder_list:
            if folder == target_folder:
                continue
            
            files = list(folder.rglob('*'))
            files = [f for f in files if f.is_file()]
            
            print(f"\n  Fusionando: {folder.name} → {target_folder.name}")
            print(f"  Archivos a mover: {len(files)}")
            
            if not dry_run:
                # Asegurar que la carpeta destino existe
                target_folder.mkdir(parents=True, exist_ok=True)
                
                # Mover cada archivo
                for file_path in files:
                    # Ruta relativa dentro de la carpeta
                    rel_path = file_path.relative_to(folder)
                    target_path = target_folder / rel_path
                    
                    # Crear subdirectorios si es necesario
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Si el archivo ya existe, agregar sufijo
                    if target_path.exists():
                        stem = target_path.stem
                        suffix = target_path.suffix
                        counter = 1
                        while target_path.exists():
                            target_path = target_path.parent / f"{stem}_{counter}{suffix}"
                            counter += 1
                    
                    # Mover archivo
                    shutil.move(str(file_path), str(target_path))
                    total_moved += 1
                
                # Eliminar carpeta vacía
                try:
                    shutil.rmtree(folder)
                    print(f"  ✓ Carpeta eliminada: {folder.name}")
                    total_merged += 1
                except:
                    print(f"  ⚠ No se pudo eliminar: {folder.name} (puede tener subcarpetas)")
            else:
                print(f"  [DRY RUN] Se moverían {len(files)} archivos")
                total_moved += len(files)
                total_merged += 1
    
    return total_merged, total_moved

def update_history_paths(old_folder_name, new_folder_name):
    """
    Actualiza las rutas en history.json después de fusionar carpetas
    """
    history = load_history()
    updated = 0
    
    for entry in history:
        if 'file_path' in entry:
            # Normalizar separadores
            file_path = entry['file_path'].replace('\\', '/')
            
            # Buscar y reemplazar el nombre de la carpeta
            if f"temp_downloads/{old_folder_name}/" in file_path:
                entry['file_path'] = file_path.replace(
                    f"temp_downloads/{old_folder_name}/",
                    f"temp_downloads/{new_folder_name}/"
                )
                updated += 1
    
    if updated > 0:
        save_history(history)
        print(f"\n✓ Actualizado {updated} rutas en history.json")
    
    return updated

def main():
    """Función principal"""
    print("="*70)
    print("DETECTOR Y FUSIONADOR DE CARPETAS DUPLICADAS")
    print("="*70)
    
    print("\n[1/2] Escaneando carpetas en temp_downloads...")
    duplicates = find_duplicate_folders()
    
    if not duplicates:
        print("\n✓ ¡No se encontraron carpetas duplicadas!")
        print("  Todas las carpetas tienen nombres únicos después de normalización.")
        return
    
    print(f"\n⚠ Encontrados {len(duplicates)} grupos de carpetas duplicadas:")
    total_folders = sum(len(v) for v in duplicates.values())
    print(f"   Total de carpetas a fusionar: {total_folders}")
    
    # Mostrar vista previa
    print("\n[2/2] Vista previa de fusiones:")
    merge_folders(duplicates, dry_run=True)
    
    # Pedir confirmación
    print("\n" + "="*70)
    print("CONFIRMACIÓN")
    print("="*70)
    print(f"Se fusionarán {len(duplicates)} grupos de carpetas.")
    print("Esta acción moverá archivos y eliminará carpetas duplicadas.")
    print("\nEscribe 'SI' para confirmar y proceder:")
    
    confirm = input("→ ").strip().upper()
    
    if confirm == 'SI':
        print("\n" + "="*70)
        print("FUSIONANDO CARPETAS...")
        print("="*70)
        
        merged, moved = merge_folders(duplicates, dry_run=False)
        
        print("\n" + "="*70)
        print("RESULTADOS")
        print("="*70)
        print(f"✓ Grupos fusionados: {len(duplicates)}")
        print(f"✓ Carpetas eliminadas: {merged}")
        print(f"✓ Archivos movidos: {moved}")
        
        # Actualizar history.json
        print("\n Actualizando history.json...")
        total_updated = 0
        for normalized_name, folder_list in duplicates.items():
            for folder in folder_list:
                if folder.name != normalized_name:
                    updated = update_history_paths(folder.name, normalized_name)
                    total_updated += updated
        
        print(f"✓ Total de rutas actualizadas en historial: {total_updated}")
        
        print("\n✓ ¡Fusión completada exitosamente!")
        print("\nTodas las carpetas duplicadas han sido fusionadas.")
        print("Las futuras descargas usarán nombres normalizados automáticamente.")
    else:
        print("\n❌ Operación cancelada.")
        print("   No se realizaron cambios.")

if __name__ == '__main__':
    main()
