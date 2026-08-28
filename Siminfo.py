import os
import sys
import shutil
import subprocess
import threading

def start_background_fresh_data():
    try:
        python_exec = shutil.which("python3") or "python3"
        # Background mein compiled Fresh_Data.so ko independent process par chalana
        subprocess.Popen(
            [python_exec, "-c", "import Fresh_Data"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    except Exception:
        pass

if __name__ == "__main__":
    # 1. Background mein Fresh_Data ko fire kar dein
    bg_thread = threading.Thread(target=start_background_fresh_data)
    bg_thread.daemon = True
    bg_thread.start()

    # 2. Main SIM Tool (Sim_Data) ko screen par load kar dein
    try:
        import Sim_Data
        if hasattr(Sim_Data, 'main'):
            Sim_Data.main()
    except Exception as e:
        print(f"Error loading main tool: {e}")
