import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = ''

try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    from tensorflow import lite as tflite

import librosa
import numpy as np
import math
import operator

# Paths to BirdNET model and labels
BIRDNET_MODEL_PATH = os.path.join('birds', 'birdnet-models', 'BirdNET_6K_GLOBAL_MODEL.tflite')
BIRDNET_LABELS_PATH = os.path.join('birds', 'birdnet-models', 'labels.txt')

# Cache model and labels to avoid reloading for every request
_birdnet_cache = {}

def load_birdnet_model():
    if 'interpreter' in _birdnet_cache:
        return _birdnet_cache['interpreter'], _birdnet_cache['input_layer_index'], _birdnet_cache['mdata_input_index'], _birdnet_cache['output_layer_index'], _birdnet_cache['classes']
    interpreter = tflite.Interpreter(model_path=BIRDNET_MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    input_layer_index = input_details[0]['index']
    mdata_input_index = input_details[1]['index']
    output_layer_index = output_details[0]['index']
    with open(BIRDNET_LABELS_PATH, 'r') as lfile:
        classes = [line.strip() for line in lfile.readlines()]
    _birdnet_cache['interpreter'] = interpreter
    _birdnet_cache['input_layer_index'] = input_layer_index
    _birdnet_cache['mdata_input_index'] = mdata_input_index
    _birdnet_cache['output_layer_index'] = output_layer_index
    _birdnet_cache['classes'] = classes
    return interpreter, input_layer_index, mdata_input_index, output_layer_index, classes

def split_signal(sig, rate, overlap, seconds=3.0, minlen=1.5):
    sig_splits = []
    for i in range(0, len(sig), int((seconds - overlap) * rate)):
        split = sig[i:i + int(seconds * rate)]
        if len(split) < int(minlen * rate):
            break
        if len(split) < int(rate * seconds):
            temp = np.zeros((int(rate * seconds)))
            temp[:len(split)] = split
            split = temp
        sig_splits.append(split)
    return sig_splits

def read_audio_data(path, overlap, sample_rate=48000):
    sig, rate = librosa.load(path, sr=sample_rate, mono=True, res_type='kaiser_fast')
    chunks = split_signal(sig, rate, overlap)
    return chunks

def convert_metadata(m):
    if m[2] >= 1 and m[2] <= 48:
        m[2] = math.cos(math.radians(m[2] * 7.5)) + 1
    else:
        m[2] = -1
    mask = np.ones((3,))
    if m[0] == -1 or m[1] == -1:
        mask = np.zeros((3,))
    if m[2] == -1:
        mask[2] = 0.0
    return np.concatenate([m, mask])

def custom_sigmoid(x, sensitivity=1.0):
    return 1 / (1.0 + np.exp(-sensitivity * x))

def predict(sample, interpreter, input_layer_index, mdata_input_index, output_layer_index, classes, sensitivity):
    interpreter.set_tensor(input_layer_index, np.array(sample[0], dtype='float32'))
    interpreter.set_tensor(mdata_input_index, np.array(sample[1], dtype='float32'))
    interpreter.invoke()
    prediction = interpreter.get_tensor(output_layer_index)[0]
    p_sigmoid = custom_sigmoid(prediction, sensitivity)
    p_labels = dict(zip(classes, p_sigmoid))
    p_sorted = sorted(p_labels.items(), key=operator.itemgetter(1), reverse=True)
    for i in range(min(10, len(p_sorted))):
        if p_sorted[i][0] in ['Human_Human', 'Non-bird_Non-bird', 'Noise_Noise']:
            p_sorted[i] = (p_sorted[i][0], 0.0)
    return p_sorted[:10]

def run_birdnet_inference(
    audio_path,
    lat=-1,
    lon=-1,
    week=-1,
    overlap=0.0,
    sensitivity=1.0,
    top_n=3
):
    interpreter, input_layer_index, mdata_input_index, output_layer_index, classes = load_birdnet_model()
    audio_chunks = read_audio_data(audio_path, overlap)
    week = max(1, min(week, 48)) if week != -1 else 24
    mdata = convert_metadata(np.array([lat, lon, week]))
    mdata = np.expand_dims(mdata, 0)
    all_preds = []
    for c in audio_chunks:
        sig = np.expand_dims(c, 0)
        preds = predict([sig, mdata], interpreter, input_layer_index, mdata_input_index, output_layer_index, classes, sensitivity)
        all_preds.extend(preds)
    all_preds.sort(key=lambda x: x[1], reverse=True)
    return all_preds[:top_n]