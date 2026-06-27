"""
Script to download timelapse images from Firebase Storage
and compile them into a video using OpenCV.
"""

import os

import cv2
import firebase_admin
from firebase_admin import credentials, storage


# Configuration Constants
DIR_NAME = "<your folder name>"
CREDENTIAL_PATH = "<your crendential.json file path>"
STORAGE_BUCKET = "<your storage bucket path>"
FPS = 25


def setup_firebase():
    """Initialize Firebase application and return the storage bucket."""
    cred = credentials.Certificate(CREDENTIAL_PATH)
    firebase_admin.initialize_app(cred, {
        "storageBucket": STORAGE_BUCKET
    })
    return storage.bucket()


def download_images(bucket, download_dir):
    """Download all JPG files from the specified Firebase directory."""
    os.makedirs(download_dir, exist_ok=True)
    blobs = bucket.list_blobs(prefix=f"{DIR_NAME}/")

    print("Starting download...")
    for blob in blobs:
        if blob.name.endswith(".jpg"):
            filename = os.path.join(download_dir, os.path.basename(blob.name))
            print(f"Downloading {blob.name} -> {filename}")
            blob.download_to_filename(filename)
            
    print("All files downloaded.")


def create_video(image_folder, output_video):
    """Read images from a directory and stitch them into an MP4 video."""
    # Collect all .jpg images sorted by filename
    images = sorted([
        img for img in os.listdir(image_folder) if img.endswith(".jpg")
    ])
    
    if not images:
        raise RuntimeError("No .jpg images found in the folder.")

    # Get frame size from the first image
    first_frame_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(first_frame_path)
    
    if frame is None:
        raise ValueError(f"Failed to read the first image: {first_frame_path}")
        
    height, width, _ = frame.shape

    # Define video writer using H264 codec
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    video = cv2.VideoWriter(output_video, fourcc, FPS, (width, height))

    # Write frames to video
    print(f"Writing {len(images)} frames to {output_video}...")
    for img_name in images:
        img_path = os.path.join(image_folder, img_name)
        frame = cv2.imread(img_path)
        
        # Only write if the image was read successfully
        if frame is not None:
            video.write(frame)

    video.release()
    print(f"Video created: {output_video}")


def main():
    """Main execution block."""
    download_dir = f"./{DIR_NAME}"
    output_video = f"{DIR_NAME}.mp4"

    bucket = setup_firebase()
    
    # Execute the pipeline
    download_images(bucket, download_dir)
    create_video(download_dir, output_video)


if __name__ == "__main__":
    main()
