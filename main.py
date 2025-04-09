import sys
import os
import time
import json
import subprocess
import shutil
# import keyboard
from pynput import keyboard
import threading

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

INPUT_DIR_PATH = "./input"
CONFIG_PATH = "./config.json"
PROCESS_PATH = None
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
                return
            print("[WATCHER] Config modify failed")
            return
 

def esc_listener(key):
    global running
    if key == keyboard.Key.esc:
        print("\n[WATCHER] ESC pressed, exiting...")
        running = False

def start_listener():
    listener = keyboard.Listener(on_press=esc_listener)
    listener.start()
    return listener
            
def get_file_count():
    files = os.listdir(INPUT_DIR_PATH)
    dir_size = sum(os.path.getsize(f) for f in files if os.path.isfile(f))
    return len(files), dir_size

def process_data(config: Config):
    print(f"[{config.process}] Running process ")
    process = subprocess.run(["py", f"{config.process}.py"])
    if process.returncode == -1:
        print(f"[FAIL] Process failed ")
        return False
    if process.returncode == 0:
        print(f"[SUCCESS] Process finished ")
        return True
    return False
    
def main():
    running = True
    
    print("[WATCHER] Starting DICOM watcher...")
    print("[WATCHER] Press ESC to exit")
    start_listener()
    
    observer = Observer()
    config = Config()
    config.load_config()
    
    observer.schedule(config, path=".", recursive=False)
    observer.start()
    
    check_value = 0
    last_dir_size = 0    
    while running:
        
        if check_value % 5 == 0:
            print("[WATCHER] Waiting...")
        
        if check_value >= CHECK_INTERVAL:
            file_count, current_dir_size = get_file_count()
            if last_dir_size != current_dir_size:
                print("[WATCHER] No files to process")
                continue
            
            print(f"[WATCHER] Found {file_count} files")
            last_dir_size = current_dir_size
            
            print(f"[{config.process}] Processing data")
            process_success = process_data(config)
            if process_success:
                print("[WATCHER] Moving files to ./processed")
                move_files()
            check_value = 0
        time.sleep(1)
        check_value += 1
    observer.stop()
    print("[WATCHER] Exiting program")

def move_files():
    files = os.listdir(INPUT_DIR_PATH)
    print(f"[WATCHER] Processed {len(files)} files")
    for f in files:
        fp = os.path.join(INPUT_DIR_PATH, f)
        shutil.move(fp, "./processed")
    print(f"[WATCHER] Moved {len(files)} to ./processed")
    
if __name__ == "__main__":
    main()
    