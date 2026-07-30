import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import time

def scan_isbn_from_image(path):
    """Scans an image for an ISBN barcode and returns the detected ISBN."""
    image = cv2.imread(path)
    if image is None:
        return None, "Could not read image"

    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    decoded_objects = decode(img)
    for obj in decoded_objects:
        isbn = obj.data.decode('utf-8')
        print(f"Found ISBN: {isbn}")
        return isbn
    return None


def scan_isbn_from_webcam(timeout_seconds=15):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None

    start_time = time.time()
    isbn = None
    try:
        while time.time() - start_time < timeout_seconds:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.flip(frame, 1)
            isbn = scan_isbn_from_image(frame)
            if isbn:
                break
    finally:
        cap.release()

    return isbn