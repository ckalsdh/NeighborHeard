#!/bin/bash
while true; do
    python3 preprocess_audio.py
    python3 email_noti.py
    sleep 10
done
