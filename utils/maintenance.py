"""
Utilidad de Mantenimiento para V128 Downloader
Escanea temp_downloads, detecta videos corruptos y sincroniza con history.json
"""

import os
import json
import subprocess
from pathlib import Path

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

def scan_downloaded_files():
    """Escanea todos los archivos en temp_downloads"""
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
    """
    Verifica la integridad de un video usando FFprobe
    Retorna: (is_valid, duration, error_msg)
    """
    try:
        # Usar ffprobe para verificar el video
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name,duration',
            '-show_entries', 'format=duration',
            '-of', 'json',
            str(file_path)
        ]
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=10,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            return False, 0, f"FFprobe error: {result.stderr[:100]}"
        
        # Parsear salida JSON
        try:
            data = json.loads(result.stdout)
            
            # Verificar que tenga streams de video
            if 'streams' in data and len(data['streams']) > 0:
                codec = data['streams'][0].get('codec_name', '')
                duration = float(data.get('format', {}).get('duration', 0))
                
                if codec and duration > 0:
                    return True, duration, None
                elif duration == 0:
                    return False, 0, "Duration is 0 (possibly corrupted)"
                else:
                    return False, 0, "No video codec found"
            else:
                return False, 0, "No video stream found"
        except json.JSONDecodeError:
            return False, 0, "Invalid FFprobe output"
            
    except subprocess.TimeoutExpired:
        return False, 0, "FFprobe timeout"
    except FileNotFoundError:
        return False, 0, "FFprobe not found (install FFmpeg)"
    except Exception as e:
        return False, 0, f"Error: {str(e)}"

def sync_history_with_files():
    """
    Sincroniza el historial con los archivos reales
    Retorna estadísticas
    """
    print("🔍 Escaneando archivos descargados...")
    files = scan_downloaded_files()
    print(f"   Encontrados: {len(files)} archivos\n")
    
    print("📖 Cargando historial...")
    history = load_history()
    print(f"   Entradas en historial: {len(history)}\n")
    
    # Crear mapa de rutas normalizadas
    file_paths = {os.path.normpath(f['path']): f for f in files}
    history_paths = {}
    
    for entry in history:
        if 'file_path' in entry and entry.get('status') == 'completed':
            normalized = os.path.normpath(entry['file_path'])
            history_paths[normalized] = entry
    
    # Archivos sin entrada en historial
    orphaned_files = []
    for path in file_paths:
        if path not in history_paths:
            orphaned_files.append(file_paths[path])
    
    # Entradas de historial sin archivo
    missing_files = []
    for path in history_paths:
        if path not in file_paths and not os.path.exists(path):
            missing_files.append(history_paths[path])
    
    print("\n📊 RESULTADOS DE SINCRONIZACIÓN:")
    print("=" * 60)
    print(f"✅ Archivos sincronizados: {len(file_paths) - len(orphaned_files)}")
    print(f"⚠️  Archivos sin historial: {len(orphaned_files)}")
    print(f"❌ Entradas sin archivo: {len(missing_files)}")
    
    if orphaned_files:
        print(f"\n⚠️  ARCHIVOS SIN REGISTRO EN HISTORIAL ({len(orphaned_files)}):")
        print("-" * 60)
        for f in orphaned_files[:10]:  # Mostrar primeros 10
            size_mb = f['size'] / (1024 * 1024)
            print(f"   📁 {f['folder']}/")
            print(f"      📄 {f['name']} ({size_mb:.2f} MB)")
        if len(orphaned_files) > 10:
            print(f"   ... y {len(orphaned_files) - 10} más")
    
    if missing_files:
        print(f"\n❌ ENTRADAS CON ARCHIVOS FALTANTES ({len(missing_files)}):")
        print("-" * 60)
        for entry in missing_files[:10]:
            print(f"   🎬 {entry.get('title', 'Unknown')[:60]}")
            print(f"      📂 {entry.get('file_path', 'No path')}")
        if len(missing_files) > 10:
            print(f"   ... y {len(missing_files) - 10} más")
    
    return {
        'total_files': len(files),
        'total_history': len(history),
        'synced': len(file_paths) - len(orphaned_files),
        'orphaned': orphaned_files,
        'missing': missing_files
    }

def check_corrupted_videos():
    """
    Verifica integridad de videos en temp_downloads
    """
    print("\n🔍 VERIFICANDO INTEGRIDAD DE VIDEOS...")
    print("=" * 60)
    print("⚠️  Esto puede tardar varios minutos dependiendo de la cantidad de archivos\n")
    
    files = scan_downloaded_files()
    video_extensions = {'.mp4', '.mkv', '.webm', '.avi', '.mov', '.flv'}
    
    videos = [f for f in files if Path(f['path']).suffix.lower() in video_extensions]
    print(f"📹 Videos encontrados: {len(videos)}\n")
    
    corrupted = []
    valid = []
    
    for i, video in enumerate(videos, 1):
        print(f"[{i}/{len(videos)}] Verificando: {video['name'][:50]}...", end='  ')
        
        is_valid, duration, error = check_video_integrity(video['path'])
        
        if is_valid:
            print(f"✅ OK ({duration:.1f}s)")
            valid.append(video)
        else:
            print(f"❌ CORRUPTO: {error}")
            corrupted.append({**video, 'error': error})
    
    print("\n" + "=" * 60)
    print(f"✅ Videos válidos: {len(valid)}")
    print(f"❌ Videos corruptos: {len(corrupted)}")
    
    if corrupted:
        print("\n❌ VIDEOS CORRUPTOS DETECTADOS:")
        print("-" * 60)
        for v in corrupted:
            size_mb = v['size'] / (1024 * 1024)
            print(f"   📁 {v['folder']}/")
            print(f"      📄 {v['name']}")
            print(f"      💾 {size_mb:.2f} MB")
            print(f"      ⚠️  {v['error']}")
            print()
    
    return corrupted, valid

def clean_orphaned_history_entries():
    """Limpia entradas del historial sin archivo correspondiente"""
    history = load_history()
    cleaned = []
    kept = []
    
    for entry in history:
        if 'file_path' in entry:
            if os.path.exists(entry['file_path']):
                kept.append(entry)
            else:
                cleaned.append(entry)
        else:
            kept.append(entry)  # Mantener entradas sin file_path (pendientes, etc)
    
    if cleaned:
        print(f"\n🧹 Limpiando {len(cleaned)} entradas huérfanas del historial...")
        save_history(kept)
        print(f"✅ Historial limpio. Entradas restantes: {len(kept)}")
    else:
        print("\n✅ No hay entradas huérfanas en el historial")
    
    return cleaned

def delete_corrupted_videos(corrupted_list):
    """Elimina videos corruptos"""
    if not corrupted_list:
        print("\n✅ No hay videos corruptos para eliminar")
        return
    
    print(f"\n⚠️  ADVERTENCIA: Se eliminarán {len(corrupted_list)} archivos corruptos")
    print("Esta acción NO se puede deshacer.\n")
    
    confirm = input("¿Continuar? (escribe 'SI' para confirmar): ")
    
    if confirm.strip().upper() == 'SI':
        deleted = 0
        for video in corrupted_list:
            try:
                os.remove(video['path'])
                print(f"🗑️  Eliminado: {video['name']}")
                deleted += 1
            except Exception as e:
                print(f"❌ Error al eliminar {video['name']}: {e}")
        
        print(f"\n✅ {deleted} archivos eliminados")
    else:
        print("\n❌ Operación cancelada")

def main_menu():
    """Menú principal"""
    print("\n" + "=" * 60)
    print("🛠️  UTILIDAD DE MANTENIMIENTO - V128 DOWNLOADER")
    print("=" * 60)
    print("\n1. 📊 Sincronizar historial con archivos")
    print("2. 🔍 Verificar integridad de videos")
    print("3. 🧹 Limpiar historial (eliminar entradas sin archivo)")
    print("4. 🗑️  Eliminar videos corruptos")
    print("5. 🔄 TODO: Sincronizar + Verificar + Limpiar")
    print("0. ❌ Salir")
    
    choice = input("\n👉 Selecciona una opción: ")
    return choice

def main():
    """Función principal"""
    corrupted_cache = []
    
    while True:
        choice = main_menu()
        
        if choice == '1':
            sync_history_with_files()
        
        elif choice == '2':
            corrupted_cache, valid = check_corrupted_videos()
        
        elif choice == '3':
            clean_orphaned_history_entries()
        
        elif choice == '4':
            if not corrupted_cache:
                print("\n⚠️  Primero ejecuta la opción 2 para verificar videos")
            else:
                delete_corrupted_videos(corrupted_cache)
                corrupted_cache = []  # Limpiar cache después de eliminar
        
        elif choice == '5':
            print("\n🔄 EJECUTANDO MANTENIMIENTO COMPLETO...\n")
            sync_history_with_files()
            corrupted_cache, valid = check_corrupted_videos()
            clean_orphaned_history_entries()
            
            print("\n" + "=" * 60)
            print("✅ MANTENIMIENTO COMPLETO FINALIZADO")
            print("=" * 60)
        
        elif choice == '0':
            print("\n👋 ¡Hasta luego!")
            break
        
        else:
            print("\n❌ Opción inválida")
        
        input("\n[Presiona ENTER para continuar]")

if __name__ == '__main__':
    main()
