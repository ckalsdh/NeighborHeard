#################################
# script to run IN Termux
##################################
import requests
import json
import time
import subprocess
from pimux import scrip
# from dotenv import load_dotenv
import os

# load_dotenv()
THINGSBOARD_URL=os.getenv('THINGSBOARD_URL')
ACCESS_TOKEN=os.getenv('ACCESS_TOKEN')
TERMUX_HOST='x.x.x.x'
TERMUX_USER='user_name'
TERMUX_PASSWORD='password'

# SSH connection details
HOST = TERMUX_HOST
PORT = 8022
USERNAME = TERMUX_USER
PASSWORD = TERMUX_PASSWORD

# ThingsBoard details
THINGSBOARD_URL = THINGSBOARD_URL
ACCESS_TOKEN = ACCESS_TOKEN

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {ACCESS_TOKEN}"}
url = f"http://{THINGSBOARD_URL}:8080/api/v1/{ACCESS_TOKEN}/telemetry"

while (1):
#while True:
    ts = time.time()
    print("Time: ", ts)
    # Run termux-audio-record to record audio for a fixed duration
    temp_audio_file_path = f"/data/data/com.termux/files/home/temp_output.wav"
    audio = scrip.compute(f"termux-microphone-record -f {temp_audio_file_path} -l 5")
    
    time.sleep(5)
    
    scrip.compute(f"scp -i 560_cal.pem {temp_audio_file_path} ubuntu@13.57.202.141:/home/ubuntu/audio_files")
    scrip.compute(f"rm {temp_audio_file_path}")

    # Delay before next iteration
    time.sleep(5)