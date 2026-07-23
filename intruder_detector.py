import cv2
import numpy as np
import time
import os
import sys
import subprocess
from datetime import datetime

# Streamlit Cloud Linux Compatibility Check
IS_WINDOWS = sys.platform.startswith('win')

if IS_WINDOWS:
    try:
        import winsound
    except Exception:
        winsound = None
else:
    winsound = None

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_DIR = os.path.join(BASE_DIR, "snapshots")
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

def show_windows_notification(title, message):
    if not IS_WINDOWS:
        return
    try:
        ps_script = f"""
        [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Warning
        $notify.BalloonTipIcon = 'Warning'
        $notify.BalloonTipText = '{message}'
        $notify.BalloonTipTitle = '{title}'
        $notify.Visible = $true
        $notify.ShowBalloonTip(5000)
        """
        subprocess.Popen(["powershell", "-Command", ps_script], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass

def play_alert_sound():
    if winsound:
        try:
            winsound.Beep(1800, 150)
            winsound.Beep(2400, 250)
        except Exception:
            pass

def main():
    print("=" * 65)
    print("   HD SMART INTRUDER SECURITY SYSTEM v2.0")
    print("=" * 65)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera not available. If running on Streamlit Cloud, please use app.py!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    prev_frame = None
    is_armed = True
    last_alert_time = 0
    cooldown = 10

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)

        motion_detected = False

        if prev_frame is not None and is_armed:
            frame_delta = cv2.absdiff(prev_frame, gray_blurred)
            thresh = cv2.threshold(frame_delta, 20, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=3)

            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) > 3500:
                    motion_detected = True
                    (x, y, cw, ch) = cv2.boundingRect(contour)
                    cv2.rectangle(frame, (x, y), (x + cw, y + ch), (0, 0, 255), 2)
                    cv2.putText(frame, "TARGET DETECTED", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        prev_frame = gray_blurred
        current_time = time.time()

        if is_armed and motion_detected and (current_time - last_alert_time > cooldown):
            last_alert_time = current_time
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            snap_path = os.path.join(SNAPSHOT_DIR, f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(snap_path, frame)
            play_alert_sound()
            show_windows_notification("HD INTRUDER ALERT", f"Intruder Motion Detected at {timestamp_str}")

        cv2.rectangle(frame, (0, 0), (w, 50), (15, 23, 42), -1)
        status_text = "INTRUDER GUARD: ARMED & ACTIVE" if is_armed else "INTRUDER GUARD: PAUSED"
        cv2.putText(frame, status_text, (20, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        try:
            cv2.imshow("Smart HD Intruder Security System", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('a'):
                is_armed = not is_armed
        except Exception:
            # Fallback for headless environments
            print("[INFO] Frame processed in Headless Environment.")
            time.sleep(0.1)

    cap.release()
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass

if __name__ == "__main__":
    main()
