#################################
# script to run IN ec2
##################################
# import torch
import numpy as np
import librosa
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict

import sys
from dotenv import load_dotenv
import json
import os
import boto3
import sagemaker

# load environment variables
load_dotenv()

# load sagemaker models
session = boto3.Session(
	aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
	aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
	region_name='us-west-2',
)
session = sagemaker.Session(boto_session=session)

endpoint_name = 'dsci560-ast-endpoint0'
predictor = sagemaker.predictor.Predictor(endpoint_name=endpoint_name, sagemaker_session=session)
predictor.serializer = sagemaker.serializers.NumpySerializer()


# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

def send_email(notification_text, house_name, is_vehicle_present, is_gunshot_present):
    """Send an email notification."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        if is_vehicle_present:
            msg['Subject'] = f"Vehicle Speeding Alert: {house_name}"
        elif is_gunshot_present:
            msg['Subject'] = f"Gunshot Detection Alert: {house_name}"
        else:
            msg['Subject'] = f"Sound Detection Alert: {house_name}"
        
        full_text = f'Sound detected at {house_name}:\n{notification_text}'
        msg.attach(MIMEText(full_text, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def preprocess_audio(file_path):
    """Preprocess audio for model input."""
    # audio, sr = librosa.load(file_path, sr=16000, mono=True)
    # audio = np.expand_dims(audio, axis=0)
    # return torch.tensor(audio, dtype=torch.float32)
    filename = os.path.basename(file_path)
    stream = librosa.stream(
        file_path,
        block_length=256,
        frame_length=1024,
        hop_length=1024)
    print(stream)
    print(type(stream))
    # result = predictor.predict(block)
    result = [predictor.predict(y_block) for y_block in stream]
    # result = [model.predict(y_block, 1) for y_block in stream]
    return result


def convert_logits_to_probabilities(data):
    result = []
    for group in data:
        converted_group = [[item[0], 1 / (1 + np.exp(-item[1]))] for item in group]
        result.append(converted_group)
    return result

def flatten_and_merge_categories(data):
    category_probabilities = defaultdict(list)

    # Iterate through the groups and inner lists to collect probabilities by category
    for group in data:
        for category, probability in group:
            category_probabilities[category].append(probability)

    # Compute the mean probability for each category
    result = [[category, sum(probabilities) / len(probabilities)]
              for category, probabilities in category_probabilities.items()]

    return result

# coordinates = {
# 	'rzi1.wav': (34.0284387, -118.2843101),
# 	'rza1.wav': (34.0283301, -118.2843078),
# 	'rzi2.wav': (34.0284379, -118.2851701),
# 	'rza2.wav': (34.0283334, -118.2851775),
# 	'mpa1.wav': (34.0285049, -118.2845733),
# 	'mpa2.wav': (34.0283109, -118.2853535),
# 	'mpi1.wav': (34.0283207, -118.2846250),
# 	'mpi2.wav': (34.0285550, -118.2853481),
# 	'mci1.wav': (34.0283501, -118.2849361),
# 	'mci2.wav': (34.0283395, -118.2856103),
# 	'mca1.wav': (34.0284193, -118.2849401),
# 	'mca2.wav': (34.0284268, -118.2856362),
# }

house_name = {
	'rzi1.wav': 'House 1',
    'rza1.wav': 'House 2',
    'rzi2.wav': 'House 3',
    'rza2.wav': 'House 4',
    'mpa1.wav': 'House 5',
    'mpa2.wav': 'House 6',
    'mpi1.wav': 'House 7',
    'mpi2.wav': 'House 8',
    'mci1.wav': 'House 9',
    'mci2.wav': 'House 10',
    'mca1.wav': 'House 11',
    'mca2.wav': 'House 12',
}
def predict_send_mail(audio_file_path):
    filename = os.path.basename(audio_file_path)
    current_coordinates = house_name.get(filename, 'House Unknown')

    result = preprocess_audio(audio_file_path)
    result = [json.loads(item.decode('utf-8')) for item in result] # convert bytes to string
    result = convert_logits_to_probabilities(result) # convert logits to probabilities
    final_result = flatten_and_merge_categories(result)
    print('Final Result: ', final_result)

    is_vehicle_present = any(item[0] == "Vehicle" for item in final_result)
    is_gunshot_present = any(item[0] == "Gunshot, gunfire" for item in final_result)
    should_send_email = any(item[0] in ["Vehicle", "Gunshot, gunfire", "Engine"] and float(item[1]) >= 0.03 for item in final_result)
    print(is_vehicle_present, is_gunshot_present, send_email)
    
    # only send email if vehicle or gunshot is present
    if should_send_email and (is_vehicle_present or is_gunshot_present):
        notification_message = ", ".join([f"({item[0]}, {item[1]:.6f})" for item in final_result])
        send_email(notification_message, 'House 19', is_vehicle_present, is_gunshot_present)
    # else:
    #     notification_message = ", ".join([f"({item[0]}, {item[1]:.6f})" for item in final_result])
    #     # Send an email notification
    #     send_email(notification_message, current_coordinates, is_vehicle_present, is_gunshot_present)

if __name__ == "__main__":
    '''
    python email_noti.py ../data/runs/run1/processed/mca1.wav
    '''
    # predict_send_mail('../data/runs/sample_mca1.mp3')
    # predict_send_mail('audio_files/audio_1731887861.7407954.mp3')
    predict_send_mail('audio_files/output.wav')

    ##########################################################################################
    ##################################### main testing #######################################
    ##########################################################################################
    # if len(sys.argv) < 2:
    #     print("Usage: python detect.py <audio_file_path>")
    #     sys.exit(1)

    # audio_file = sys.argv[1]
    # filename = os.path.basename(audio_file)
    # current_coordinates = house_name.get(filename, 'House Unknown')

    # result = preprocess_audio(audio_file)
    # result = [json.loads(item.decode('utf-8')) for item in result] # convert bytes to string
    # result = convert_logits_to_probabilities(result) # convert logits to probabilities
    # final_result = flatten_and_merge_categories(result)
    # print('Final Result: ', final_result)

    # # sorted_data = sorted(result, key=lambda x: x[0][1], reverse=True)
    # # print('Sorted Result: ', sorted_data)
    
    # #############################
    # # if tuple inside the list
    # #############################
    # # is_vehicle_present = any(item[0][0] == "Vehicle" for item in final_result)
    # # is_gunshot_present = any(item[0][0] == "Gunshot, gunfire" for item in final_result)
    # # notification_message = ", ".join([f"({item[0][0]}, {item[0][1]:.6f})" for item in final_result])

    # #############################
    # # for list inside the list
    # #############################
    # is_vehicle_present = any(item[0] == "Vehicle" for item in final_result)
    # is_gunshot_present = any(item[0] == "Gunshot, gunfire" for item in final_result)
    # notification_message = ", ".join([f"({item[0]}, {item[1]:.6f})" for item in final_result])

    # #############################
    # # email test
    # # notification_message = 'hello world'
    # # print(notification_message)
    # #############################
    
    # # Send an email notification
    # send_email(notification_message, current_coordinates, is_vehicle_present, is_gunshot_present)
