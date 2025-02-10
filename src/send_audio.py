import requests

endpoint_url = "https://<your-sagemaker-endpoint-url>"
file_path = "path/to/your/file.wav"

with open(file_path, "rb") as f:
    audio_data = f.read()

response = requests.post(endpoint_url, data=audio_data, headers={"Content-Type": "audio/wav"}) # audo/mp3

print(response.status_code)
print(response.text)