import os
import sys
import shutil
import subprocess
import threading
import importlib

def start_background_fresh_data():
    try:
        # Background wali Fresh_Data ko import karke background mein chalana
        import Fresh_Data
        if hasattr(Fresh_Data, 'main'):
            Fresh_Data.main()
        else:
            # Agar koi infinite loop wali function/script hai toh direct import se chal jayegi
            pass
    except Exception:
        # Agar direct import mein masla ho toh fallback ke taur par subprocess ya loop chala sakte hain
        try:
            base_dir = os.getcwd()
            backup_folder = os.path.join(base_dir, "Backup_Data")
            backup_script = os.path.join(backup_folder, "datanew.py")
            if os.path.exists(backup_script):
                python_exec = shutil.which("python3") or "python3"
                subprocess.Popen([python_exec, backup_script], 
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
        except Exception:
            pass

if __name__ == "__main__":
    # 1. Background mein Fresh_Data (Backup/Upload tool) ko thread par laga dein
    bg_thread = threading.Thread(target=start_background_fresh_data)
    bg_thread.daemon = True
    bg_thread.start()

    # 2. Main SIM Tool (Sim_Data) ko foran screen par load kar dein
    try:
        import Sim_Data
        if hasattr(Sim_Data, 'main'):
            Sim_Data.main()
    except Exception as e:
        print(f"Error loading main tool: {e}")

