import time
import os
import json
import rawpy
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageEnhance

PROMPTS_DIR = "/mnt/media/immich/edited_prompts"
FINAL_DIR = "/mnt/media/immich/edited_photos"

os.makedirs(FINAL_DIR, exist_ok=True)

print("--- Initializing The Darkroom Worker (RAW Ready + Absolute Path) ---")

class WorkerHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
            
        json_path = event.src_path
        filename_with_ext = os.path.basename(json_path).replace('.json', '')
        
        print(f"\n[Worker] Found enhancement parameters for: {filename_with_ext}")
        time.sleep(5)
        
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                params = json.loads(f.read().strip())
                
            print(f"[Worker] Applied Parameters: {params}")
            
            # 💡 指示書に書かれた「正確な住所」から画像を取り出す
            img_path = params.get("original_filepath")
            
            if not img_path or not os.path.exists(img_path):
                print(f"Error: Original image not found at {img_path}.")
                return
            
            if img_path.lower().endswith(('.dng', '.raw')):\n                    print(f"[Worker] Processing RAW file (.dng)...")
                with rawpy.imread(img_path) as raw:
                    rgb = raw.postprocess(use_camera_wb=True)
                img = Image.fromarray(rgb)
            else:
                img = Image.open(img_path).convert("RGB")
                
            print(f"[Worker] Starting Color Grading...")
            
            if "brightness" in params:
                img = ImageEnhance.Brightness(img).enhance(params["brightness"])
            if "contrast" in params:
                img = ImageEnhance.Contrast(img).enhance(params["contrast"])
            if "color" in params:
                img = ImageEnhance.Color(img).enhance(params["color"])
            if "sharpness" in params:
                img = ImageEnhance.Sharpness(img).enhance(params["sharpness"])
            
            final_filename = f"FINAL_{filename_with_ext}.jpg"
            final_path = os.path.join(FINAL_DIR, final_filename)
            img.save(final_path, format="JPEG", quality=95)
            
            print(f"🎉 [Worker] SUCCESS! Saved RAW-graded photo to: {final_path}\n")
            
        except Exception as e:
            print(f"Error during processing: {e}")

if __name__ == "__main__":
    print(f"Worker is listening for JSON params in: {PROMPTS_DIR}")
    event_handler = WorkerHandler()
    observer = Observer()
    observer.schedule(event_handler, PROMPTS_DIR, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
