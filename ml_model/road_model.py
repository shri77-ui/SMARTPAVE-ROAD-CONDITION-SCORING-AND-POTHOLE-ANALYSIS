import cv2
import numpy as np

def detect_road_damage(image_path, save_path):
    img = cv2.imread(image_path)
    if img is None:
        return "Unknown", 0, 0, 0

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    h, w = gray.shape
    image_area = h * w

    # =====================
    # CRACK DETECTION
    # =====================
    edges = cv2.Canny(blur, 80, 160)
    edges = cv2.morphologyEx(edges, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    crack_pixels = np.sum(edges > 0)
    crack_ratio = crack_pixels / edges.size

    img[edges > 0] = [0, 0, 255]  # red cracks

    # =====================
    # POTHOLE DETECTION (DEPTH BASED)
    # =====================
    laplacian = cv2.Laplacian(blur, cv2.CV_64F)
    laplacian = np.absolute(laplacian)
    laplacian = np.uint8(laplacian)

    _, pothole_mask = cv2.threshold(laplacian, 30, 255, cv2.THRESH_BINARY)
    pothole_mask = cv2.morphologyEx(
        pothole_mask, cv2.MORPH_CLOSE, np.ones((7,7), np.uint8), iterations=2
    )

    contours, _ = cv2.findContours(
        pothole_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    pothole_area = 0
    pothole_count = 0

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 0.01 * image_area:
            continue

        hull = cv2.convexHull(cnt)
        hull_area = cv2.contourArea(hull)

        if hull_area == 0:
            continue

        solidity = area / hull_area

        if solidity < 0.6:
            continue

        x, y, bw, bh = cv2.boundingRect(cnt)

        cv2.rectangle(img, (x, y), (x + bw, y + bh), (0, 0, 255), 3)
        cv2.putText(
            img, "POTHOLE",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2
        )

        pothole_area += area
        pothole_count += 1

    pothole_ratio = pothole_area / image_area

    # =====================
    # FINAL SCORE + OUTPUT
    # =====================
    if pothole_count > 0:
        label = "Pothole Detected"
        score = max(10, int(100 - pothole_ratio * 400))
    elif crack_ratio < 0.004:
        label = "Good Road"
        score = 90
    elif crack_ratio < 0.015:
        label = "Cracked Road"
        score = 65
    else:
        label = "Severe Cracks"
        score = 40

    cv2.imwrite(save_path, img)

    return label, score, round(crack_ratio * 100, 2), round(pothole_ratio * 100, 2)
