import os
import torch
import sqlite3
from datetime import datetime
from pathlib import Path
from PIL import Image

# Load YOLOv5 custom model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)

# Paths
input_folder = 'screenshots'
output_folder = 'screenshots/detections'
os.makedirs(output_folder, exist_ok=True)

# Connect to the database
conn = sqlite3.connect('violations.db')
cursor = conn.cursor()

# Ensure table exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS helmet_violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_path TEXT,
        timestamp TEXT,
        plate_number TEXT
    )
''')
conn.commit()

# Dummy number plate (can be replaced with OCR in realtime)
def extract_fake_number_plate(image_path):
    return "TN01AB1234"

# Process all images
for img_file in os.listdir(input_folder):
    if img_file.endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(input_folder, img_file)
        results = model(img_path)
        results.save(save_dir=output_folder)

        predictions = results.pandas().xyxy[0]
        labels = predictions['name'].tolist()

        if 'no helmet' in labels:
            print(f"[🚫] No helmet detected in: {img_file}")
            
            # Save to DB
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            plate_number = extract_fake_number_plate(img_path)  # Placeholder
            cursor.execute('INSERT INTO helmet_violations (image_path, timestamp, plate_number) VALUES (?, ?, ?)',
                           (img_path, timestamp, plate_number))
            conn.commit()
        else:
            print(f"[✅] Helmet worn in: {img_file}")

conn.close()
print("\n✅ Detection and logging complete.")