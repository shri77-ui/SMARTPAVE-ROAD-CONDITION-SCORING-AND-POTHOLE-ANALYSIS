from flask import Flask, render_template, request, Response
import cv2
import os
from ultralytics import YOLO
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ===== MODEL =====
model = YOLO("best.pt")   # <-- YOUR TRAINED MODEL

# ===== CAMERA =====
camera = cv2.VideoCapture(0)
camera_active = False
mail_sent = False

# ===== EMAIL CONFIG =====
EMAIL_SENDER = "shri97450@gmail.com"
EMAIL_PASSWORD = "dkcbeaaagqykpknc"
EMAIL_RECEIVER = "shri67610@gmail.com"

# ===== LOGIC =====
def severity_level(potholes):
    if potholes == 0:
        return "Low"
    elif potholes <= 2:
        return "Medium"
    else:
        return "High"

def road_health_score(potholes, severity):
    score = 100 - potholes * 10
    if severity == "Medium":
        score -= 10
    elif severity == "High":
        score -= 30
    return max(score, 0)

def send_alert_email(potholes, severity, health):
    msg = EmailMessage()
    msg["Subject"] = "🚨 SmartPave Pothole Alert"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    msg.set_content(f"""
SMARTPAVE ALERT 🚧

Potholes Detected: {potholes}
Severity: {severity}
Road Health Score: {health}/100

Immediate maintenance required.
""")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# ===== ROUTES =====
@app.route("/")
def index():
    return render_template(
        "index.html",
        potholes=0,
        severity="Low",
        health=100
    )

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    results = model(path)[0]
    boxes = results.boxes

    potholes = len(boxes)
    severity = severity_level(potholes)
    health = road_health_score(potholes, severity)

    if potholes > 0 and severity != "Low":
        send_alert_email(potholes, severity, health)

    img = cv2.imread(path)

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(img, "Pothole", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imwrite(os.path.join(STATIC_FOLDER, "detected.jpg"), img)

    return render_template(
        "index.html",
        potholes=potholes,
        severity=severity,
        health=health,
        image="detected.jpg"
    )

# ===== CAMERA CONTROL =====
@app.route("/start_camera")
def start_camera():
    global camera_active, mail_sent
    camera_active = True
    mail_sent = False
    return ("", 204)

@app.route("/stop_camera")
def stop_camera():
    global camera_active
    camera_active = False
    return ("", 204)

def gen_frames():
    global camera_active, mail_sent

    while True:
        if not camera_active:
            continue

        success, frame = camera.read()
        if not success:
            break

        results = model(frame)[0]
        boxes = results.boxes

        potholes = len(boxes)
        severity = severity_level(potholes)
        health = road_health_score(potholes, severity)

        if potholes > 0 and severity == "High" and not mail_sent:
            send_alert_email(potholes, severity, health)
            mail_sent = True

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.putText(frame, f"Potholes: {potholes}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Severity: {severity}", (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Health: {health}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/video")
def video():
    return Response(gen_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame")

# ===== RUN =====
if __name__ == "__main__":
    app.run(debug=True)
