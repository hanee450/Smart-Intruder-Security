import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import time
import requests
from datetime import datetime

st.set_page_config(
    page_title="Smart Intruder Security System",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Smart Webcam Intruder Security System")
st.markdown("Cloud & Web Security Motion Detection Dashboard")

# Sidebar Configuration
st.sidebar.header("⚙️ System Configuration")
is_armed = st.sidebar.checkbox("ARM Security System", value=True)
motion_threshold = st.sidebar.slider("Motion Sensitivity", min_value=10, max_value=50, value=25)
telegram_token = st.sidebar.text_input("Telegram Bot Token (Optional)", type="password")
telegram_chat_id = st.sidebar.text_input("Telegram Chat ID (Optional)")

st.sidebar.markdown("---")
st.sidebar.info("💡 Tip: Click 'Take Photo' or enable live stream to detect motion & intruders.")

# Session State for Snapshots
if "snapshots" not in st.session_state:
    st.session_state.snapshots = []

# Main Camera Section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Live Camera Stream")
    img_file_buffer = st.camera_input("Capture Camera Frame for Motion Inspection")

    if img_file_buffer is not None:
        # Convert buffer to PIL & OpenCV Format
        bytes_data = img_file_buffer.getvalue()
        cv_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

        # Convert to Gray & Detect Motion
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)

        # Simple motion threshold visualization
        thresh = cv2.threshold(blurred, motion_threshold, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for c in contours:
            if cv2.contourArea(c) > 1500:
                motion_detected = True
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(cv_img, (x, y), (x + w, y + h), (0, 0, 255), 3)
                cv2.putText(cv_img, "TARGET DETECTED", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # Display Analyzed Frame
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        st.image(rgb_img, caption="Analyzed Security Feed", use_container_width=True)

        if motion_detected and is_armed:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.error(f"⚠️ INTRUDER MOTION DETECTED at {timestamp}!")
            
            # Save snapshot to state
            st.session_state.snapshots.append({
                "time": timestamp,
                "image": rgb_img
            })

            # Send Telegram Alert if configured
            if telegram_token and telegram_chat_id:
                try:
                    url = f"https://api.telegram.org/bot{telegram_token}/sendPhoto"
                    _, img_encoded = cv2.imencode('.jpg', cv_img)
                    files = {'photo': img_encoded.tobytes()}
                    data = {'chat_id': telegram_chat_id, 'caption': f"⚠️ INTRUDER ALERT DETECTED at {timestamp}"}
                    requests.post(url, data=data, files=files, timeout=5)
                    st.success("📩 Telegram Alert Sent!")
                except Exception as e:
                    st.warning(f"Telegram alert failed: {e}")

with col2:
    st.subheader("📸 Captured Snapshots")
    if len(st.session_state.snapshots) == 0:
        st.info("No security alerts triggered yet.")
    else:
        for idx, snap in enumerate(reversed(st.session_state.snapshots)):
            st.image(snap["image"], caption=f"Alert #{len(st.session_state.snapshots) - idx} - {snap['time']}")
