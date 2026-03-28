import cv2
import random

def detect_damage(input_data):
    if isinstance(input_data, str):
        image = cv2.imread(input_data)
    else:
        image = input_data.copy()

    h, w, _ = image.shape

    # Fake detection box (replace with YOLO later)
    x1, y1 = random.randint(50, 150), random.randint(50, 150)
    x2, y2 = x1 + 150, y1 + 100

    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    cv2.putText(image, "Pothole", (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    score = random.randint(50, 95)

    return image, score



def calculate_score(count):
    if count == 0:
        return 100, "Road is Good"
    elif count <= 2:
        return 70, "Minor Damage"
    elif count <= 5:
        return 40, "Moderate Damage"
    else:
        return 10, "Severe Damage"


