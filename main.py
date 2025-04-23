# Imports
import time
import subprocess
import functions as f
import os

API_URL = "https://calify.pythonanywhere.com/api"
API_KEY = "bd8e4d538dfa993960152da646"

PROJECT_PATH = "/home/team46/"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PATH = PROJECT_PATH + "test_env/bin/python"
PROCESS_PATH = os.path.join(CURRENT_DIR, "process.py")

def main():
    id = f.get_id_from_file()
    print("ID:", id)

    if f.is_registered(id):
        print("The id is registered")
    else:
        print("The id is now registered")

    while(not f.is_operating(id) or not f.is_connected_to_internet()):
        time.sleep(5)

    process = subprocess.Popen([VENV_PATH, PROCESS_PATH])

    while(True):
        if not f.is_operating(id) or f.check_status(id) == 4:
            break

        time.sleep(5)
    
    process.terminate()
    process.wait()
        

if __name__ == "__main__":
    while(True):
        main()
