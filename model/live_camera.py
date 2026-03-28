import cv2
import threading
from ultralytics import YOLO
from model.email_alert import send_email
import os
import time

camera_running = False
camera_thread = None
last_score = 100

def camera_loop():
    global camera_running, last_score

    model = YOLO("model/pothole_yolov8.pt")
    cap = cv2.VideoCapture(0)

    while camera_running:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        detections = 0

        for r in results:
            detections = len(r.boxes)

        if detections > 0:
            os.makedirs("static/alerts", exist_ok=True)
            img_path = "static/alerts/alert.jpg"
            cv2.imwrite(img_path, frame)

            last_score = max(10, 100 - detections * 20)
            send_email(img_path)

        time.sleep(1)

    cap.release()

def start_camera():
    global camera_running, camera_thread
    if not camera_running:
        camera_running = True
        camera_thread = threading.Thread(target=camera_loop)
        camera_thread.start()

def stop_camera():
    global camera_running
    camera_running = False

def get_score():
    return last_score
