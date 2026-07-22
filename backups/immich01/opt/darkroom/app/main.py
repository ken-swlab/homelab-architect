import time
import os
import json
import google.generativeai as genai
from watchdog.observers.polling import PollingObserver as Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image
import rawpy

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

WATCH_DIR = "/mnt/media/immich/library"
OUTPUT_DIR = "/mnt/media/immich/edited_prompts"

os.makedirs(WATCH_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MASTER_PROMPT = """
You are a master professional photographer and colorist.
Analyze this photo taken in Scandinavia.
Determine the optimal adjustment parameters to enhance this photo.
Output ONLY a valid JSON object with float values (1.0 means no change). 
Example: {"brightness": 1.1, "contrast": 1.2, "color": 1.15, "sharpness": 1.1}
"""

class PhotoHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        
        filepath = event.src_path
        filename = os.path.basename(filepath)
        
        if not filename.lower().endswith(('.dng', '.raw')):
            return 
            
        print(f"--- Detected: {filepath} ---")
        time.sleep(10)
        
        try:
            print("Action: Developing RAW for preview...")
            with rawpy.imread(filepath) as raw:
                rgb = raw.postprocess(half_size=True)
            img = Image.fromarray(rgb)
                
            img.thumbnail((1024, 1024))
            
            print("Action: Asking Gemini for Color Grading parameters...")
            response = model.generate_content([MASTER_PROMPT, img])
            prompt_result = response.text.strip().replace("```json", "").replace("```", "").strip()
            
            # 💡 AIの答え（JSON）に、「正確な住所」を追記する！
            params = json.loads(prompt_result)
            params["original_filepath"] = filepath
            
            print(f"Result (Parameters):\n{params}\n")
            
            out_file = os.path.join(OUTPUT_DIR, f"{filename}.json")
            with open(out_file, "w") as f:
                json.dump(params, f)
                
            print(f"Success: Saved parameters to {out_file}")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Darkroom Watcher (RAW Ready + Absolute Path) is now running.")
    event_handler = PhotoHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
