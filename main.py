import csv
import cv2
import time
import os
import serial
import select
import sys
import threading
from datetime import datetime

try:
    from detector import PlateDetector
    from ocr_engine import OCRReader
except ImportError as e:
    print(f"❌ Lỗi import: {e}")
    exit()

import serial
ser = None
try:
    ser = serial.Serial('COM4', 115200, timeout=1)  # Đổi COM4 nếu cần
    print("Đã kết nối ESP32 thành công qua Serial!")
except serial.SerialException as e:
    print("Không kết nối được ESP32 → kiểm tra lại cổng hoặc chạy chế độ thay thế")
    print(f"Lỗi: {e}")

def clean_plate_text(text):
    if not text:
        return ""
    text = text.upper().strip()
    allowed = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ-."
    return "".join(c for c in text if c in allowed)

exit_flag = False

def terminal_listener():
    global exit_flag
    while True:
        cmd = input("").strip().lower()
        if cmd == "q":
            print("🔴 Đang thoát chương trình…")
            exit_flag = True
            break

listener_thread = threading.Thread(target=terminal_listener, daemon=True)
listener_thread.start()

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

print("Đang khởi tạo mô hình...")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "best.pt")

detector = PlateDetector(MODEL_PATH)

ocr_reader = OCRReader()
print("Hệ thống đã sẵn sàng!")

print("📌 Gõ 'q' trong terminal để thoát chương trình")

save_dir = "auto_captured"
os.makedirs(save_dir, exist_ok=True)

csv_file = os.path.join(BASE_DIR, "plates.csv")

if not os.path.exists(csv_file):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Thời gian", "Biển số"])

while True:

    if exit_flag:
        break

    ret, frame = cap.read()
    if not ret:
        print("❌ Không đọc được camera")
        break

    detect_result = detector.detect(frame)

    plate_img = None
    coords = None

    if detect_result:
        plate_img, box = detect_result[0]
        x1, y1, x2, y2 = box
        coords = (x1, y1, x2 - x1, y2 - y1)

    if plate_img is not None and plate_img.size > 0:
        x, y, w, h = coords

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        print("🔄 Đang đọc biển số... vui lòng chờ...")

        raw_text = ocr_reader.read_text(plate_img)
        clean_text = clean_plate_text(raw_text)

        if clean_text:
            print(f"✅ Đã nhận dạng biển số: {clean_text}")

            with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    clean_text
                ])

            print("Đã lưu vào plates.csv")

            if ser:
                try:
                    ser.write((clean_text + '\n').encode())
                    print("📤 Đã gửi xuống STM32")
                except:
                    print("⚠ Không gửi được Serial")

cap.release()
if ser:
    ser.close()
print("Đã tắt hệ thống.")