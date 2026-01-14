from paddleocr import PaddleOCR
import cv2
import logging
import warnings
import os
from datetime import datetime
import numpy as np

logging.getLogger("ppocr").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

class OCRReader:
    def __init__(self, lang='en', conf_threshold=0.3):
        print("Đang tải PaddleOCR...")
        
        self.ocr = PaddleOCR(use_angle_cls=True, lang=lang) 
        
        self.conf_threshold = conf_threshold
        
        self.save_folder = "saved_plates"
        os.makedirs(self.save_folder, exist_ok=True)
            
        print("Đã tải xong PaddleOCR.")

    def preprocess_image(self, img):
        try:
            return cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        except Exception:
            return img

    def read_text(self, plate_img):
        try:
            if plate_img is None or plate_img.size == 0:
                print("OCR: plate_img rỗng")
                return ""

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{self.save_folder}/plate_{timestamp}.jpg"
            cv2.imwrite(filename, plate_img)

            processed = self.preprocess_image(plate_img)

            result = self.ocr.ocr(processed)

            if not result or not isinstance(result, list):
                return ""

            data = result[0]

            rec_texts  = data.get("rec_texts", [])
            rec_scores = data.get("rec_scores", [])

            found = []
            for text, score in zip(rec_texts, rec_scores):
                if score >= 0.1:
                    found.append(text)

            raw = "".join(found)
            clean = "".join(c for c in raw if c.isalnum()).upper()

            if clean:
                print(f"Đã lưu: {filename} | Đọc được: {clean}")

            return clean

        except Exception as e:
            print("Lỗi trong OCR:", e)
            return ""