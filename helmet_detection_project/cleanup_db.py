import os
import sqlite3

conn = sqlite3.connect("violations.db")
cursor = conn.cursor()

cursor.execute("SELECT id, image_path FROM helmet_violations")
rows = cursor.fetchall()

for row in rows:
    id, img_path = row
    if not os.path.exists(img_path):
        print(f"[❌] File missing: {img_path} — Deleting entry.")
        cursor.execute("DELETE FROM helmet_violations WHERE id = ?", (id,))

conn.commit()
conn.close()
print("✅ Cleanup done.")