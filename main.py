# Imports
import time
import subprocess
import functions as f

API_URL = "https://calify.pythonanywhere.com/api"
API_KEY = "bd8e4d538dfa993960152da646"

def main():
    id = f.get_id_from_file()
    print("ID:", id)

    if f.is_registered(id):
        print("The id is registered")
    else:
        print("The id is now registered")

    while(not f.is_operating(id)):
        time.sleep(5)

    process = subprocess.Popen(["python", "process.py"])

    while(True):
        if not f.is_operating(id) or f.check_status(id) == 4:
            break

        time.sleep(5)
    
    process.terminate()
    process.wait()
    f.stop_process()
        

if __name__ == "__main__":
    main()