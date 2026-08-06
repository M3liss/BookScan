import os
import time

import cv2
from PIL import Image
from pyzbar.pyzbar import decode


def scan_isbn_from_image(image_or_path):
    """Scan an image path or an already-loaded image array for an ISBN barcode."""
    if image_or_path is None:
        return None

    if isinstance(image_or_path, (str, os.PathLike)):
        image = cv2.imread(str(image_or_path))
    else:
        image = image_or_path

    if image is None:
        return None

    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    decoded_objects = decode(img)
    for obj in decoded_objects:
        isbn = obj.data.decode("utf-8")
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