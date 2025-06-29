🪖 Real-Time Helmet Detection System:
A real-time computer vision system to **detect motorcycle riders without helmets**, capture violations, recognize number plates, reject deepfake/fake faces, and generate live alerts & reports.

Features:
- YOLO-based Helmet Detection**
- Voice Alerts** for violations
- Capture Images** of violators
- OCR (Number Plate)** Recognition using EasyOCR
- Deepfake / Fake Face Rejection**
- Live Statistics Dashboard** using Streamlit
- Violator Image Storage** with SQLite logging

Tech Stack:

| Component           | Tech/Library                 |
|---------------------|-----------------------------|
| Helmet Detection    | YOLOv5 / OpenCV             |
| OCR (Number Plate)  | EasyOCR, OpenCV             |
| Face Validation     | DeepFace / Custom CNN       |
| Voice Alerts        | `pyttsx3`                   |
| GUI Dashboard       | Streamlit                   |
| Database            | SQLite                      |
| Language            | Python                      |

How It Works:
1. YOLO detects people riding bikes.
2. If **helmet not detected**, capture image.
3. Play **alert sound** using `pyttsx3`.
4. Extract bike **number plate** using OCR.
5. Check face using **DeepFace** to block fake ones.
6. Store violation details in SQLite DB.
7. Show Live Dashboard** (Helmet %, count, images).

Run Locally:
1. Create virtual environment
   
2. Install dependencies
pip install -r requirements.txt

3. Run the app
streamlit run dashboard.py


Output Samples:
Helmet          Action Taken
YES✅            No alert
No❌             Image captured, alert played, DB logged


