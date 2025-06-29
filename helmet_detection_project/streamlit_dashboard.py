import streamlit as st
import sqlite3
import pandas as pd
import os
from PIL import Image

st.set_page_config(page_title="🪖 Helmet Violation Dashboard", layout="wide")

st.title("🪖 Helmet Violation Live Dashboard")

# Load data from DB
def load_data():
    conn = sqlite3.connect("violations.db")
    df = pd.read_sql_query("SELECT * FROM helmet_violations ORDER BY timestamp DESC", conn)
    conn.close()
    return df

df = load_data()

# Search Box
search = st.text_input("🔍 Search by Number Plate", "")
filtered_df = df[df['number_plate'].str.contains(search.upper())] if search else df

st.write(f"📊 Total Violations: {len(filtered_df)}")

# Show data table
st.dataframe(filtered_df[['timestamp', 'number_plate', 'image_path']], use_container_width=True)

# Show images
st.subheader("📸 Violation Images")
for i, row in filtered_df.iterrows():
    img_path = row['image_path']
    if os.path.exists(img_path):
        st.image(img_path, caption=f"{row['timestamp']} | {row['number_plate']}", width=300)

# Download CSV
csv = filtered_df.to_csv(index=False)
st.download_button(label="📥 Download Violations as CSV", data=csv, file_name="helmet_violations.csv", mime="text/csv")

#  to run project 
# python test_yolo.py
# python helmet_detect_realtime.py
# streamlit run streamlit_dashboard.py