# PiLapse: Raspberry Pi Cloud Timelapse

A lightweight, efficient timelapse camera solution built for the Raspberry Pi. This project captures images, annotates them with timestamps and author details, and uploads them directly to Firebase Storage.

A secondary script is provided to download these images to your local machine and compile them into an MP4 video.

## Features

* **Zero SD Card Wear:** Images are temporarily saved to the Raspberry Pi's RAM disk (`/dev/shm`) before uploading. The local file is immediately deleted after a successful upload, meaning no writes are made to your SD card, vastly extending its lifespan.
* **Auto-Annotation:** Automatically stamps the image with the date, time, and camera details.
* **Automated Cloud Backup:** Uploads directly to Firebase Storage.
* **Video Compilation:** Includes an OpenCV script to stitch downloaded images into an H.264 video.

## Hardware & OS Tested

* **Board:** Raspberry Pi Zero 2 W
* **Camera:** 5MP OV5647 (Standard Pi Camera Module)
* **OS:** Raspberry Pi OS (Trixie)

## Prerequisites: Firebase Setup

Before running the code, you must set up a Firebase project:

1. Go to the Firebase Console and create a project.
2. Enable Firebase Storage.
3. Generate a service account key by going to Project Settings -> Service Accounts -> Generate new private key.
4. Rename the downloaded file to `credential.json` (or `.service.json`) and place it in the same directory as your scripts.
5. Update the STORAGE_BUCKET variable in the scripts with your actual Firebase bucket URL.

## Installation & Setup

Because this project relies on picamera2 which communicates directly with the Pi's hardware, you must install the camera libraries system-wide and then give your virtual environment access to them.

**1. Install System Dependencies**<br>
Run these commands in your terminal:
```
sudo apt update
sudo apt install python3-picamera2
```

**2. Create a Virtual Environment**<br>
You must create the virtual environment using the system-site-packages flag so it can access the picamera2 library we just installed globally:
```
python3 -m venv venv --system-site-packages
```

**3. Activate the Virtual Environment**
```
source venv/bin/activate
```

**4. Install Python Requirements**
```
pip install -r requirements.txt
```

## Usage

**1. Capture & Upload (Run on the Raspberry Pi)**<br>
Run the capture script to begin taking photos. It will run in a continuous loop, taking a photo every 5 seconds, uploading it, and clearing it from RAM.
```
python main.py
```
*(Press Ctrl+C to safely stop the timelapse).*

**2. Download & Compile (Run on your local PC)**<br>
Once your timelapse is finished, run the compiler script on your main computer to download the images from Firebase and stitch them into an MP4 video.
```
python video.py
```

---
