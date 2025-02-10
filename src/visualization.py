# %%
import os
import time
from itertools import cycle
import librosa
import folium
from folium.plugins import MarkerCluster
from tqdm import tqdm

from model import predict
# %%
runs = ['run1', 'run2']
runpaths = {}
for run in runs:
	filepaths = []
	for file in os.listdir(f"../data/runs/{run}/processed"):
		if file.endswith('.wav'):
			filepath = os.path.join(f"../data/runs/{run}/processed", file)
			filepaths.append(filepath)
	runpaths[run] = filepaths

full_results = {}
for run, filepaths in runpaths.items():
	results = {}
	for filepath in tqdm(filepaths):
		filename = os.path.basename(filepath)
		stream = librosa.stream(
			filepath,
			block_length=256,
			frame_length=1024,
			hop_length=1024)
		result = [predict(y_block, 1) for y_block in stream]
		results[filename] = result
	full_results[run] = results
# %%
length = min([len(item) for key, item in full_results['run1'].items()])
for key, item in full_results['run2'].items():
	full_results['run2'][key] = item[:length]
full_results
# %%
coordinates = {
	'rzi1.wav': (34.0284387, -118.2843101),
	'rza1.wav': (34.0283301, -118.2843078),
	'rzi2.wav': (34.0284379, -118.2851701),
	'rza2.wav': (34.0283334, -118.2851775),
	'mpa1.wav': (34.0285049, -118.2845733),
	'mpa2.wav': (34.0283109, -118.2853535),
	'mpi1.wav': (34.0283207, -118.2846250),
	'mpi2.wav': (34.0285550, -118.2853481),
	'mci1.wav': (34.0283501, -118.2849361),
	'mci2.wav': (34.0283395, -118.2856103),
	'mca1.wav': (34.0284193, -118.2849401),
	'mca2.wav': (34.0284268, -118.2856362),
}
# %%
data = {}
for run, results in full_results.items():
	for item, result in results.items():
		data[item] = result

data
# %%
[(key, item[1][0][0]) for key, item in data.items()]
# %%
for i in range(length):
	coords = coordinates[filename]
	labels = [(key, item[i][0][0]) for key, item in data.items()]
	map_center = [34.0284, -118.2849]
	folium_map = folium.Map(location=map_center, zoom_start=18)
	marker_cluster = MarkerCluster().add_to(folium_map)
	for label in labels:
		folium.Marker(location=coordinates[label[0]], popup=f"{label[0]}: {label[1]}").add_to(marker_cluster)
		time.sleep(2)
		folium_map.save('progressive_map.html')