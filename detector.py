from ultralytics import YOLO
import cv2
import numpy as np

class PlateDetector:
    def __init__(self, model_path='best.pt', conf_threshold=0.5):
        print(f"Đang tải YOLO model ({model_path})...")
        try:
            self.model = YOLO(model_path)
            self.conf_threshold = conf_threshold
            print("Đã tải xong YOLO.")
        except Exception as e:
            print(f"Lỗi tải model YOLO: {e}")
            self.model = None

    def detect(self, frame):
        if self.model is None: return []

        results = self.model.predict(frame, stream=True, verbose=False, conf=self.conf_threshold)
        detected_plates = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                h, w, _ = frame.shape
                crop_y1, crop_y2 = max(0, y1-5), min(h, y2+5)
                crop_x1, crop_x2 = max(0, x1-5), min(w, x2+5)
                
                plate_crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
                
                if plate_crop.size > 0:
                    detected_plates.append((plate_crop, (x1, y1, x2, y2)))
        
        return detected_plates