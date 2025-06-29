import sqlite3

conn = sqlite3.connect("violations.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS helmet_violations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    number_plate TEXT,
    image_path TEXT
)
''')

# Add missing columns (only if not already added)
try:
    cursor.execute("ALTER TABLE helmet_violations ADD COLUMN latitude TEXT")
except:
    pass

try:
    cursor.execute("ALTER TABLE helmet_violations ADD COLUMN longitude TEXT")
except:
    pass

conn.commit()
conn.close()
print("✅ Table initialized and columns ensured.")