import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import time

def scan_isbn_from_image(image):
    """Scans an image for an ISBN barcode and returns the detected ISBN."""
    # Convert OpenCV image to PIL format
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    # Decode the barcode(s) from the image
    decoded_objects = decode(img)

    # Iterate over detected barcodes
    for obj in decoded_objects:
        # Extract the data (barcode value), assuming it's an ISBN
        isbn = obj.data.decode('utf-8')
        print(f"Found ISBN: {isbn}")
        return isbn
    return None

def scan_isbn_from_webcam():
    """Continuously captures frames from webcam and scans for an ISBN."""
    cap = cv2.VideoCapture(0)
    print("Scanning for ISBN... Press 'q' to exit.")
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting...")
            break
        
        frame = cv2.flip(frame, 1)  # Flip horizontally (mirror effect)


        # Call the existing function to process the frame
        isbn = scan_isbn_from_image(frame)

        # Draw a visual cue if an ISBN is found
        if isbn:
            cv2.imshow("ISBN Scanner", frame)
            cv2.waitKey(1000)  # Pause for 2 seconds before resuming
            break

        # Display the video feed
        cv2.imshow("ISBN Scanner", frame)

        # Exit on pressing 'q'
        end_time = time.time()
        if cv2.waitKey(1) & 0xFF == ord('q') or end_time - start_time > 10:
            break

    cap.release()
    cv2.destroyAllWindows()
    return isbn

#scan_isbn_from_webcam()
