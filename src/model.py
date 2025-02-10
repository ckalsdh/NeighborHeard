import torch
from tqdm import tqdm
from transformers import ASTFeatureExtractor
from transformers import AutoModelForAudioClassification

SAMPLING_RATE = 16000
feature_extractor = ASTFeatureExtractor()
model = AutoModelForAudioClassification.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")

def predict(waveform, k=5):
	inputs = feature_extractor(
		waveform,
		sampling_rate=SAMPLING_RATE,
		padding='max_length',
		return_tensors='pt'
	).input_values

	with torch.no_grad():
		outputs = model(inputs)

	topk_values, topk_indices = outputs.logits.topk(k, dim=-1)
	top_predictions = [
		(model.config.id2label[idx.item()], val.item()) \
		for idx, val in zip(topk_indices[0], topk_values[0])
	]
	return top_predictions