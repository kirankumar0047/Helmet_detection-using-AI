# helmet_streamlit_app.py
import streamlit as st
import cv2
import torch
import os
import pandas as pd
import sqlite3
import easyocr
from datetime import datetime
import geocoder
from PIL import Image
import tempfile

# Set page layout
st.set_page_config(page_title="Helmet Detection Live Dashboard", layout="wide")

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)

# EasyOCR reader
reader = easyocr.Reader(['en'])

# Database setup
DB_PATH = "violations.db"
def create_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS helmet_violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            number_plate TEXT,
            image_path TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# Save violation to DB
def save_violation(img, plate_text):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"screenshots/no_helmet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    cv2.imwrite(filename, img)

    # Get live location
    g = geocoder.ip('me')
    lat, lon = g.latlng if g.latlng else (0.0, 0.0)

    # Store in DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO helmet_violations (timestamp, number_plate, image_path, latitude, longitude) VALUES (?, ?, ?, ?, ?)",
              (timestamp, plate_text, filename, lat, lon))
    conn.commit()
    conn.close()

# Real-time detection
def detect_violations():
    cap = cv2.VideoCapture(0)
    stframe = st.empty()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        labels, coords = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]

        for i, row in enumerate(coords):
            x1, y1, x2, y2, conf = row[:5]
            label = int(labels[i])
            if conf < 0.5:
                continue

            x1, y1, x2, y2 = int(x1 * frame.shape[1]), int(y1 * frame.shape[0]), int(x2 * frame.shape[1]), int(y2 * frame.shape[0])
            cropped = frame[y1:y2, x1:x2]
            label_text = results.names[label]

            color = (0, 255, 0) if label_text == "helmet" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            if label_text == "no_helmet":
                # Run OCR to detect number plate
                ocr_result = reader.readtext(cropped)
                plate_text = ocr_result[0][1] if ocr_result else "Unknown"
                save_violation(frame, plate_text)

        stframe.image(frame, channels='BGR', use_column_width=True)

    cap.release()

# Sidebar menu
st.sidebar.title("🪖 Helmet Detection Dashboard")
menu = st.sidebar.radio("Choose an option", ["Live Detection", "View Violations"])

# Option 1: Live detection
if menu == "Live Detection":
    st.subheader("🔴 Real-time Helmet Violation Detection")
    st.warning("Click the button below to start webcam and detect violations in real-time.")
    if st.button("Start Camera"):
        detect_violations()

# Option 2: View violation table
elif menu == "View Violations":
    st.subheader("📋 Violation Records")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM helmet_violations ORDER BY timestamp DESC", conn)
    conn.close()

    if df.empty:
        st.info("No violations recorded yet.")
    else:
        st.dataframe(df)

        st.subheader("📸 Violation Images")
        for index, row in df.iterrows():
            st.markdown(f"**Time:** {row['timestamp']} | **Plate:** {row['number_plate']} | 📍Location: ({row['latitude']}, {row['longitude']})")
            st.image(row["image_path"], width=400)

             # to run this project
             # streamlit run helmet_streamlit_app.py