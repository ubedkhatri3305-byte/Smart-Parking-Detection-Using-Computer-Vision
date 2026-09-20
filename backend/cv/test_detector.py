import sys
import cv2
from backend.cv.yolo_detector import ParkingYOLODetector

def main():
    img_path = sys.argv[1] if len(sys.argv) > 1 else "backend/data/scenarios/scenario_1_aerial.jpg"
    img = cv2.imread(img_path)
    if img is None:
        print(f"Error loading image {img_path}")
        return

    print(f"Loaded image: {img_path}, dimensions: {img.shape[1]}x{img.shape[0]}")
    detector = ParkingYOLODetector()
    detections = detector.detect(img)
    print(f"Total objects detected: {len(detections)}")
    for d in detections:
        print(f" - [{d['category'].upper()}] {d['class_name']}: {d['confidence']*100:.1f}% | bbox: {d['bbox']}")

if __name__ == "__main__":
    main()
