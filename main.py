import sys
import os
import time
import json
import subprocess
import shutil
import keyboard
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INPUT_DIR_PATH = "./input"
CONFIG_PATH = "./config.json"
PROCESS_PATH = None

def reload_config():
    print("config updated")
    return True


class ConfigHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("config.json"):
            code = reload_config()
            if code:
                print("[WATCHDOG] Config update success")
            else:
                print("[WATCHDOG] Config update failed")

if len(sys.argv) == 2:
    INPUT_DIR_PATH = sys.argv[1]

last_config_time = 0
model_name = None
running = True

def esc_listener():
    global running
    keyboard.wait('esc')
    print("\n[WATCHER] ESC pressed, exiting...")
    running = False

listener_thread = threading.Thread(target=esc_listener, daemon=True)
listener_thread.start()

def load_config():
    global model_name, last_config_time
    if os.path.exists(CONFIG_PATH):
        mod_time = os.path.getmtime(CONFIG_PATH)
        if mod_time != last_config_time:
            with open(CONFIG_PATH) as file:
                config_file = json.load(file)
                model_name = config_file["model"]
                print(f"[CONFIG] Using model: {model_name}")
            last_config_time = mod_time
            
def get_folder_size():
    total = 0
    files = os.listdir(INPUT_DIR_PATH)
    total = sum(os.path.getsize(f) for f in files if os.path.isfile(f))
        # fp = os.path.join(INPUT_DIR_PATH, f)
    return total, len(files)

def is_transfer_done(dir_path, wait_time=5, retries=3):
    for _ in range(retries):
        last_size, _ = get_folder_size()
        time.sleep(wait_time)
        current_size, files_count = get_folder_size()
        if current_size != last_size:
            continue
        else:
            return True, files_count
    return False, 0

def process_data():
    print(f"[PROCESSING] Running process ")
    process = subprocess.run(["py", "dcm2mha.py"])
    if process.returncode == -1:
        print(f"[FAIL] Process failed ")
        return False
    if process.returncode == 0:
        print(f"[SUCCESS] Process finished ")
        return True
    return False
    
def main():
    print("[WATCHER] Starting DICOM watcher...")
    print("[WATCHER] Press ESC to exit")
    observer = Observer()
    observer.schedule(ConfigHandler(), path=".", recursive=False)
    observer.start()
    
    while running:
        load_config()
        transfer_done, files_count = is_transfer_done(INPUT_DIR_PATH)
        if transfer_done and files_count > 0:
            print(f"[WATCHER] Found {files_count} files")
            process_success = process_data()
            if process_success:
                print(f"[WATCHER] Processed {files_count} files")
                files = os.listdir(INPUT_DIR_PATH)
                for f in files:
                    fp = os.path.join(INPUT_DIR_PATH, f)
                    # shutil.move(fp, "./processed")
                print(f"[WATCHER] Moved {files_count} to ./processed")
        else:
            print("[WATCHER] No files to process")
        # time.sleep(2)
    observer.stop()
    print("[WATCHER] Exiting program")
    
if __name__ == "__main__":
    main()
    