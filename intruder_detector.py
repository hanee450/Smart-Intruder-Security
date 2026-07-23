import cv2
import numpy as np
import time
import os
import sys
import subprocess
import winsound
from datetime import datetime

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SNAPSHOT_DIR = os.path.join(BASE_DIR, "snapshots")
if not os.path.exists(SNAPSHOT_DIR):
    os.makedirs(SNAPSHOT_DIR)

def show_windows_notification(title, message):
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
    try:
        winsound.Beep(1800, 150)
        winsound.Beep(2400, 250)
    except Exception:
        pass

def draw_rounded_rect(img, pt1, pt2, color, thickness=1, r=10):
    x1, y1 = pt1
    x2, y2 = pt2
    w = x2 - x1
    h = y2 - y1

    # Draw Corner Brackets (Cyberpunk Style)
    length = min(w, h) // 4
    # Top-Left
    cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness + 1)
    cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness + 1)
    # Top-Right
    cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness + 1)
    cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness + 1)
    # Bottom-Left
    cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness + 1)
    cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness + 1)
    # Bottom-Right
    cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness + 1)
    cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness + 1)

def main():
    print("=" * 65)
    print("   HD SMART INTRUDER SECURITY SYSTEM v2.0 (ULTRA QUALITY)")
    print("=" * 65)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Camera not available.")
        return

    # Request Full HD 1080p Output
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, 60)

    prev_frame = None
    is_armed = True
    last_alert_time = 0
    cooldown = 10
    last_snapshot_crop = None

    fps_start_time = time.time()
    fps_counter = 0
    fps = 60

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Calculate FPS
        fps_counter += 1
        if time.time() - fps_start_time >= 1.0:
            fps = fps_counter
            fps_counter = 0
            fps_start_time = time.time()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray_blurred = cv2.GaussianBlur(gray, (25, 25), 0)

        motion_detected = False
        target_box = None

        if prev_frame is not None and is_armed:
            frame_delta = cv2.absdiff(prev_frame, gray_blurred)
            thresh = cv2.threshold(frame_delta, 20, 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=3)

            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            max_area = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 3500:
                    motion_detected = True
                    if area > max_area:
                        max_area = area
                        (x, y, cw, ch) = cv2.boundingRect(contour)
                        target_box = (x, y, x + cw, y + ch)

            if motion_detected and target_box:
                (x1, y1, x2, y2) = target_box
                # Draw Futuristic Target Box
                draw_rounded_rect(frame, (x1, y1), (x2, y2), (0, 0, 255), thickness=2)
                cv2.rectangle(frame, (x1, y1 - 25), (x1 + 180, y1), (0, 0, 200), -1)
                cv2.putText(frame, "TARGET DETECTED", (x1 + 8, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Capture Crop Inset Preview
                if x2 - x1 > 20 and y2 - y1 > 20:
                    crop = frame[y1:y2, x1:x2]
                    if crop.size > 0:
                        last_snapshot_crop = cv2.resize(crop, (120, 120))

        prev_frame = gray_blurred
        current_time = time.time()
        time_since_alert = current_time - last_alert_time

        # Trigger Security Action
        if is_armed and motion_detected and time_since_alert > cooldown:
            last_alert_time = current_time
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            filename = f"intruder_hd_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            snap_path = os.path.join(SNAPSHOT_DIR, filename)

            # High Quality Snapshot Write
            cv2.imwrite(snap_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            print(f"[HD SECURITY ALERT] Snapshot Saved: {snap_path}")

            play_alert_sound()
            show_windows_notification("HD INTRUDER ALERT", f"Intruder Motion Detected at {timestamp_str}")
            try:
                os.startfile(snap_path)
            except Exception:
                pass

        # ---------------- SLEEK UI OVERLAY ----------------
        # Top Glassmorphism Bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), (15, 23, 42), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)

        # Status Indicator Dot
        dot_color = (0, 0, 255) if (is_armed and motion_detected) else ((0, 255, 0) if is_armed else (100, 100, 100))
        cv2.circle(frame, (30, 30), 10, dot_color, -1)
        cv2.circle(frame, (30, 30), 14, dot_color, 2)

        status_text = "INTRUDER GUARD: ARMED & ACTIVE" if is_armed else "INTRUDER GUARD: PAUSED"
        cv2.putText(frame, status_text, (55, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"FPS: {fps} | 1080p HD", (w - 180, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)

        # PiP Preview Box for Last Intruder Crop
        if last_snapshot_crop is not None:
            cv2.rectangle(frame, (w - 150, h - 160), (w - 20, h - 30), (0, 0, 255), 2)
            frame[h - 150:h - 30, w - 140:w - 20] = last_snapshot_crop
            cv2.putText(frame, "LAST TARGET", (w - 145, h - 165), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1)

        # Bottom Bar
        cv2.rectangle(frame, (0, h - 30), (w, h), (0, 0, 0), -1)
        cv2.putText(frame, "Press [A] to Arm/Disarm | Press [Q] to Exit HD Mode", (20, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Smart HD Intruder Security System 2.0", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('a'):
            is_armed = not is_armed

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
