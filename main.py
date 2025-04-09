import sys
import os
import time
import json
import subprocess
import shutil
from pynput import keyboard

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INPUT_DIR_PATH = "./input"
CONFIG_PATH = "./config.json"
PROCESSED_PATH = "./processed"
CHECK_INTERVAL = 20

def reload_config():
    print("config updated")
    return True


class Config(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.model = None
        
    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH) as file:
                config_file = json.load(file)
                self.process = config_file["process"]
                self.unet_name = config_file["unet_name"]
                return True
            return False
    
    def on_modified(self, event):
        if event.src_path.endswith("config.json"):
            if self.load_config():
                print("[WATCHER] Config modified")
                return None
            print("[WATCHER] Config modify failed")
            return None
 

# def esc_listener(key):
#     global running
#     if key == keyboard.Key.esc:
#         print("\n[WATCHER] ESC pressed, exiting...")
#         running = False

# def start_listener():
#     listener = keyboard.Listener(on_press=esc_listener)
#     listener.start()
#     return listener
            
def get_file_count():
    files = os.listdir(INPUT_DIR_PATH)
    dir_size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))
    return len(files), dir_size

def process_data(config: Config):
    print(f"[{config.process}] Running process ")
    process = None
    try:
        process = subprocess.run([sys.executable, f"{config.process}.py"], check=True)
    except subprocess.CalledProcessError as er:
        print(f"Script {config.process} failed with exit code {er.returncode}")
    
    if process is None:
        return False
    
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
    # start_listener()
    
    observer = Observer()
    config = Config()
    config.load_config()
    
    # observer.schedule(config, path=".", recursive=False)
    # observer.start()
    
    check_value = 0
    last_dir_size = 0    
    while True:
        
        if check_value % 5 == 0:
            print("[WATCHER] Idle...")
        
        if check_value >= CHECK_INTERVAL:
            file_count, current_dir_size = get_file_count()
            if last_dir_size != current_dir_size:
                print("[WATCHER] No files to process")
                continue
            
            print(f"[WATCHER] Found {file_count} files")
            
            if file_count > 0:
                print(f"[{config.process}] Processing data")
                process_success = process_data(config)
                if process_success:
                    print("[WATCHER] Moving files to ./processed")
                    move_files()
                
            check_value = 0
            last_dir_size = current_dir_size
        
        time.sleep(1)
        check_value += 1
    # observer.stop()
    # print("[WATCHER] Exiting program")

def move_files():
    files = os.listdir(INPUT_DIR_PATH)
    print(f"[WATCHER] Processed {len(files)} files")
    for f in files:
        src_fp = os.path.join(INPUT_DIR_PATH, f)
        dest_fp = os.path.join(PROCESSED_PATH, f)
        if os.path.exists(dest_fp):
            print(f"File \"{dest_fp}\" exists, overwriting")
        shutil.move(src_fp, dest_fp)
    print(f"[WATCHER] Moved {len(files)} to ./processed")
    
if __name__ == "__main__":
    main()
    