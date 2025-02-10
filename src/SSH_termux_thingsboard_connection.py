import paramiko
# import pysftp
from dotenv import load_dotenv
import os

load_dotenv()

# SSH connection details
HOST = os.getenv('TERMUX_HOST')
PORT = 8022
USERNAME = os.getenv('TERMUX_USER')
PASSWORD = os.getenv('TERMUX_PASSWORD')

# Thingsboard details
THINGSBOARD_URL = os.getenv('THINGSBOARD_URL')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def execute_sensor_script(ssh_client):
    command = f"""
    python3 - <<END
import subprocess
import requests
import json
import time

def get_sensor_data(sensor_type="K6DS3TR Accelerometer"):
    command = ["termux-sensor", "-s", sensor_type, "-n", "1"]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    data_json = json.loads(result.stdout)
    sensor_values = data_json.get(sensor_type, {{}}).get('values', [0, 0, 0])
    return {{ "accelerometer_x": sensor_values[0], "accelerometer_y": sensor_values[1], "accelerometer_z": sensor_values[2] }}

def post_to_thingsboard(data):
    headers = {{ 'Content-Type': 'application/json', 'Authorization': f'Bearer {ACCESS_TOKEN}' }}
    url = "{THINGSBOARD_URL}/api/v1/{ACCESS_TOKEN}/telemetry"
    requests.post(url, headers=headers, data=json.dumps(data))

while True:
    data = get_sensor_data()
    if data:
        post_to_thingsboard(data)
    time.sleep(5)
END
    """
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    if error:
        print("Error:", error)
    else:
        print("Output:", output)

# Set up SSH client and connect to Termux
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USERNAME, password=PASSWORD,
               allow_agent=False,
               look_for_keys=False,
               timeout=10)
               #family=paramiko.AF_INET)

# cnopts = pysftp.CnOpts()
# cnopts.hostkeys = None
# with pysftp.Connection(host=HOST, port=PORT, username=USERNAME, password=PASSWORD, cnopts=cnopts) as sftp:
#     print("Connection successful!")

# execute the sensor data collection and posting script on Termux
try:
    execute_sensor_script(client)
finally:
    client.close()