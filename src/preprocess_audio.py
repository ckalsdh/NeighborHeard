#################################
# script to run IN ec2
##################################
from pimux import scrip

# convert wav to correct wav format
scrip.compute("ffmpeg -y -i audio_files/temp_output.wav -ar 44100 -ac 1 audio_files/output.wav")
