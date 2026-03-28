import cv2
from ultralytics import YOLO
from email_alert import send_email

model = YOLO(r"C:\SMARTPAVE_WEB\pothole_dataset\runs\detect\train2\weights\best.pt")

def live_camera():
    cap = cv2.VideoCapture(0)
    alert_sent = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated = results[0].plot()

        pothole_count = len(results[0].boxes)

        cv2.imshow("Pothole Detection", annotated)

        # 📧 Send Email ONCE
        if pothole_count > 0 and not alert_sent:
            image_path = "alert.jpg"
            cv2.imwrite(image_path, annotated)
            send_email(image_path)
            alert_sent = True
            print("📧 Email Alert Sent")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
