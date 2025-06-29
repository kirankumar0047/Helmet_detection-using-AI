import cv2
import torch
import easyocr
import sqlite3
import os
from datetime import datetime

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)
model.conf = 0.5  # confidence threshold

# EasyOCR reader
reader = easyocr.Reader(['en'])

# Ensure screenshots folder exists
os.makedirs("screenshots", exist_ok=True)

# Start webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    detections = results.pandas().xyxy[0]

    for index, row in detections.iterrows():
        xmin, ymin, xmax, ymax = int(row['xmin']), int(row['ymin']), int(row['xmax']), int(row['ymax'])
        label = row['name']
        conf = row['confidence']

        # Draw bounding box and label
        color = (0, 255, 0) if label == 'helmet' else (0, 0, 255)
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)
        cv2.putText(frame, f"{label} {conf:.2f}", (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # If no helmet, capture number plate and save info
        if label == 'no_helmet':
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            img_name = f"screenshots/no_helmet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(img_name, frame)

            print(f"[⚠️] No helmet detected. Saved image: {img_name}")

            # OCR for number plate (optional area: full frame or roi)
            result = reader.readtext(frame)
            plate_text = "Unknown"

            if result:
                plate_text = result[0][-2]  # Take top detection text

            print(f"[🔠] Detected Plate: {plate_text}")

            # Save to database
            conn = sqlite3.connect('violations.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO helmet_violations (timestamp, number_plate, image_path) VALUES (?, ?, ?)",
                           (timestamp, plate_text, img_name))
            conn.commit()
            conn.close()

    cv2.imshow("Helmet Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()