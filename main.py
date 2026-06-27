"""
Script to capture images from a Raspberry Pi Camera, annotate them,
and upload them to Firebase Storage.
"""

import datetime
import os
import time

import firebase_admin
from firebase_admin import credentials, storage
from picamera2 import Picamera2
from PIL import Image, ImageDraw, ImageFont


# === Configuration Constants ===
CREDENTIAL_PATH = "<your crendential.json file path>"
STORAGE_BUCKET = "<your storage bucket path>"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SIZE = 48
RESOLUTION = (2560, 1440)
UPLOAD_FOLDER = "<your folder name>"
INTERVAL_SECONDS = 5


def setup_firebase():
    """Initialize Firebase application and return the storage bucket."""
    cred = credentials.Certificate(CREDENTIAL_PATH)
    firebase_admin.initialize_app(cred, {
        "storageBucket": STORAGE_BUCKET
    })
    return storage.bucket()


def setup_camera():
    """Initialize and configure the Raspberry Pi camera."""
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": RESOLUTION})
    picam2.configure(config)
    picam2.start()
    return picam2


def capture_and_annotate(picam2):
    """Capture an image, annotate it with text, and save it to RAM."""
    now = datetime.datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M-%S.jpg")
    annotated_path = f"/dev/shm/{filename}"

    # Capture image as a PIL-compatible array
    image_array = picam2.capture_array()
    image = Image.fromarray(image_array).convert("RGB")
    
    # Flip image upside down
    image = image.transpose(Image.ROTATE_180)
    
    width, height = image.size

    # Load font and calculate dynamic box height
    font = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)
    bbox = font.getbbox("Ag")
    text_height = bbox[3] - bbox[1]
    box_height = text_height + 24

    draw = ImageDraw.Draw(image)
    
    # Draw white banner at the bottom
    draw.rectangle(
        [(0, height - box_height), (width, height)], 
        fill="white"
    )

    # Text values
    timestamp_str = now.strftime("%Y-%m-%d %H:%M:%S")
    left_text = "Shot on Raspberry Pi Camera"
    center_text = "by Rohan"
    right_text = timestamp_str

    # Draw left text
    left_coords = (20, height - box_height + 12)
    draw.text(left_coords, left_text, font=font, fill="black")

    # Draw center text
    center_x = (width - draw.textlength(center_text, font=font)) // 2
    center_coords = (center_x, height - box_height + 12)
    draw.text(center_coords, center_text, font=font, fill="black")

    # Draw right text
    right_x = width - draw.textlength(right_text, font=font) - 20
    right_coords = (right_x, height - box_height + 12)
    draw.text(right_coords, right_text, font=font, fill="black")

    image.save(annotated_path)
    return annotated_path, filename


def upload_to_firebase(bucket, filepath, filename):
    """Upload the annotated image to Firebase Storage with metadata."""
    blob = bucket.blob(f"{UPLOAD_FOLDER}/{filename}")
    
    blob.metadata = {
        "camera": "ov5647",
        "device": "Raspberry Pi",
        "author": "Rohan",
        "timestamp": filename.replace(".jpg", "")
    }
    
    blob.upload_from_filename(filepath)
    blob.patch()  # Ensure metadata is saved
    
    print(f"[{datetime.datetime.now()}] Uploaded: {filename} with metadata")


def main():
    """Main execution loop for capturing and uploading timelapse images."""
    bucket = setup_firebase()
    picam2 = setup_camera()

    try:
        while True:
            annotated_path, filename = capture_and_annotate(picam2)
            upload_to_firebase(bucket, annotated_path, filename)
            
            # Clean up image from RAM to prevent memory leaks
            os.remove(annotated_path)
            
            time.sleep(INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        picam2.stop()
        print("\n[INFO] Timelapse stopped.")


if __name__ == "__main__":
    main()
