import os
import json
import sqlite3
import shutil
import base64
import tempfile
import logging

# Try imports
try:
    import win32crypt
    import win32file
    import win32con
except ImportError:
    win32crypt = None
    win32file = None
    win32con = None

try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None

logger = logging.getLogger(__name__)

def get_encryption_key(local_state_path):
    if not win32crypt:
        logger.error("pywin32 not installed. Cannot decrypt cookies.")
        return None
        
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        # Remove DPAPI prefix
        key = key[5:] 
        # Decrypt key with DPAPI
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
    except Exception as e:
        logger.error(f"Error getting encryption key from {local_state_path}: {e}")
        return None

def decrypt_data(data, key):
    try:
        iv = data[3:15]
        data = data[15:]
        if AES:
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(data)[:-16].decode('utf-8')
        else:
            logger.error("pycryptodome not installed. Cannot decrypt AES cookies.")
            return ""
    except Exception:
        # Try without GCM (older versions or different encryption)
        try:
             return win32crypt.CryptUnprotectData(data, None, None, None, 0)[1].decode('utf-8')
        except Exception:
            return ""

def shadow_copy(src, dst):
    """
    Copies a file using win32file to bypass locking (FILE_SHARE_READ|WRITE|DELETE).
    Falls back to shutil.copy2 if win32file is unavailable.
    Includes retry logic.
    """
    import time
    
    retries = 3
    for attempt in range(retries):
        if win32file:
            try:
                hSrc = win32file.CreateFile(
                    src,
                    win32con.GENERIC_READ,
                    win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                    None,
                    win32con.OPEN_EXISTING,
                    0,
                    None
                )
                
                with open(dst, 'wb') as fDst:
                    # Get file size (used to determine read loop below)
                    _size = win32file.GetFileSize(hSrc)
                    win32file.SetFilePointer(hSrc, 0, win32con.FILE_BEGIN)
                    
                    chunk_size = 64 * 1024
                    while True:
                        hr, data = win32file.ReadFile(hSrc, chunk_size)
                        if hr == 0 and not data: break
                        if len(data) == 0: break
                        fDst.write(data)

                win32file.CloseHandle(hSrc)
                return True
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(1) # Wait 1s and retry
                    continue
                logger.warning(f"Shadow copy (win32) failed for {src}: {e}. Trying fallback.")
        
        # Fallback
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            logger.error(f"Shadow copy fallback failed for {src}: {e}")
            
    return False

def extract_cookies_to_file(browser_name, target_domain=None):
    """
    Extracts cookies from the specified browser (Brave, Chrome, Edge) 
    by copying the database to avoid locks.
    """
    
    # Paths (Windows)
    appdata = os.environ['LOCALAPPDATA']
    paths = {
        'brave': {
            'cookies': [
                os.path.join(appdata, r'BraveSoftware\Brave-Browser\User Data\Default\Network\Cookies'),
                os.path.join(appdata, r'BraveSoftware\Brave-Browser\User Data\Default\Cookies')
            ],
            'local_state': os.path.join(appdata, r'BraveSoftware\Brave-Browser\User Data\Local State')
        },
        'chrome': {
            'cookies': [
                os.path.join(appdata, r'Google\Chrome\User Data\Default\Network\Cookies'),
                os.path.join(appdata, r'Google\Chrome\User Data\Default\Cookies')
            ],
            'local_state': os.path.join(appdata, r'Google\Chrome\User Data\Local State')
        },
        'edge': {
            'cookies': [
                os.path.join(appdata, r'Microsoft\Edge\User Data\Default\Network\Cookies'),
                os.path.join(appdata, r'Microsoft\Edge\User Data\Default\Cookies')
            ],
            'local_state': os.path.join(appdata, r'Microsoft\Edge\User Data\Local State')
        }
    }

    if browser_name.lower() not in paths:
        logger.error(f"Unsupported browser: {browser_name}")
        return None

    browser_paths = paths[browser_name.lower()]
    local_state_path = browser_paths['local_state']
    
    if not os.path.exists(local_state_path):
        logger.error(f"Local State file not found for {browser_name}")
        return None

    # Get Encryption Key
    key = get_encryption_key(local_state_path)
    if not key:
        return None

    # Find valid cookie DB
    cookie_db_path = None
    for p in browser_paths['cookies']:
        if os.path.exists(p):
            cookie_db_path = p
            break
            
    if not cookie_db_path:
        logger.error(f"No cookie file found for {browser_name}")
        return None

    # Setup Temp Files
    temp_dir = tempfile.gettempdir()
    temp_db = os.path.join(temp_dir, f"{browser_name}_cookies_shadow.db")
    
    # Copy DB (Shadow Copy)
    if not shadow_copy(cookie_db_path, temp_db):
        return None
        
    # Copy WAL and SHM if they exist (important for open browsers!)
    wal_path = cookie_db_path + "-wal"
    shm_path = cookie_db_path + "-shm"
    temp_wal = temp_db + "-wal"
    temp_shm = temp_db + "-shm"
    
    if os.path.exists(wal_path):
        shadow_copy(wal_path, temp_wal)
    
    if os.path.exists(shm_path):
        shadow_copy(shm_path, temp_shm)

    # Extract
    output_file = os.path.join(temp_dir, f"{browser_name}_extracted_cookies.txt")
    conn = None
    try:
        conn = sqlite3.connect(temp_db)
        
        # If WAL mode, we might need to checkpoint? 
        # Usually just reading is fine if we have the WAL file.
        
        cursor = conn.cursor()
        
        query = "SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value FROM cookies"
        if target_domain:
            query += f" WHERE host_key LIKE '%{target_domain}%'"
            
        cursor.execute(query)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This file is generated by MiDownloader\n\n")
            
            for host_key, name, value, path, expires_utc, is_secure, is_httponly, encrypted_value in cursor.fetchall():
                if not value and encrypted_value:
                    value = decrypt_data(encrypted_value, key)
                
                if not value: continue # Skip empty
                
                flag = "TRUE" if host_key.startswith('.') else "FALSE"
                secure = "TRUE" if is_secure else "FALSE"
                
                # Expiration (Windows uses microseconds since 1601-01-01)
                # Unix uses seconds since 1970-01-01
                # Difference is 11644473600 seconds
                try:
                    expr = int((expires_utc / 1000000) - 11644473600)
                    if expr < 0: expr = 0 
                except Exception:
                    expr = 0
                    
                line = f"{host_key}\t{flag}\t{path}\t{secure}\t{expr}\t{name}\t{value}\n"
                f.write(line)
        
        return output_file

    except Exception as e:
        logger.error(f"Error reading cookies from shadow DB: {e}")
        return None
    finally:
        if conn: conn.close()
        # Cleanup
        for f in [temp_db, temp_wal, temp_shm]:
            if os.path.exists(f):
                try: os.remove(f)
                except Exception: pass

if __name__ == "__main__":
    print("Testing Cookie Extraction...")
    if not win32file: print("WARNING: pywin32 not found. Lock bypass will fail.")
    if not AES: print("WARNING: pycryptodome not found. Decryption will fail.")
    
    path = extract_cookies_to_file('brave')
    if path:
        print(f"Success! Cookies saved to: {path}")
    else:
        print("Failed to extract cookies.")
