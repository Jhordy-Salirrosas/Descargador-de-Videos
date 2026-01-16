import json
import os
import shutil
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
OLD_DOWNLOADS_DIR = os.path.join(BASE_DIR, 'temp_downloads')

def migrate():
    # 1. Load Config
    if not os.path.exists(CONFIG_FILE):
        logger.error("No config.json found!")
        return

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        target_dir = config.get('download_path')

    if not target_dir:
        logger.error("No download_path in config!")
        return

    if not os.path.exists(OLD_DOWNLOADS_DIR):
        logger.error(f"Old downloads dir not found: {OLD_DOWNLOADS_DIR}")
        return
    
    # Create target if not exists
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        logger.info(f"Created target directory: {target_dir}")

    # 2. Load History
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)

    # 3. Move Folders/Files
    logger.info(f"Moving files from {OLD_DOWNLOADS_DIR} to {target_dir}...")
    
    moved_count = 0
    updated_history_count = 0

    # Iterate over items in old temp_downloads
    for item_name in os.listdir(OLD_DOWNLOADS_DIR):
        source_path = os.path.join(OLD_DOWNLOADS_DIR, item_name)
        dest_path = os.path.join(target_dir, item_name)

        try:
            if os.path.isdir(source_path):
                # Check if dest already exists
                if os.path.exists(dest_path):
                    # Merge directories? For safety, we might skip or rename.
                    # Simple strategy: Copytree with dirs_exist_ok=True then remove source
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    shutil.rmtree(source_path)
                    logger.info(f"Merged/Moved folder: {item_name}")
                else:
                    shutil.move(source_path, dest_path)
                    logger.info(f"Moved folder: {item_name}")
            else:
                if not os.path.exists(dest_path):
                     shutil.move(source_path, dest_path)
                     logger.info(f"Moved file: {item_name}")
                else:
                    logger.warning(f"File already exists in target, skipping: {item_name}")

            moved_count += 1

        except Exception as e:
            logger.error(f"Failed to move {item_name}: {e}")

    # 4. Update History Paths
    logger.info("Updating history paths...")
    for entry in history:
        old_path = entry.get('file_path')
        if old_path and OLD_DOWNLOADS_DIR in old_path:
            # Replace prefix
            # Normalize slashes for replacement check
            # BUT we need to be careful with string replacement.
            # Best way: relative path calculation
            
            try:
                rel_path = os.path.relpath(old_path, OLD_DOWNLOADS_DIR)
                if not rel_path.startswith('..'):
                    new_path = os.path.join(target_dir, rel_path)
                    entry['file_path'] = new_path
                    updated_history_count += 1
            except ValueError:
                continue # Path not strictly inside old dir (maybe already somewhere else)

    # 5. Save History
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    logger.info(f"Migration Complete.")
    logger.info(f"Items moved (root level): {moved_count}")
    logger.info(f"History entries updated: {updated_history_count}")
    
    # 6. Remove old dir if empty
    if not os.listdir(OLD_DOWNLOADS_DIR):
        os.rmdir(OLD_DOWNLOADS_DIR)
        logger.info("Removed empty temp_downloads directory.")

if __name__ == "__main__":
    migrate()
