import os
import librosa
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import matplotlib.pyplot as plt
import subprocess
import time
from gpiozero import LED
from scipy.signal import butter, lfilter
import warnings
warnings.filterwarnings("ignore")

# Constants
SAMPLE_RATE = 8000
TOTAL_RECORD_TIME = 15  # Record 15 seconds
KEEP_LAST_SECONDS = 10  # Keep only last 10 seconds
SEGMENT_LENGTH = 10     # Processed segment length
N_MELS = 64
FMAX = 4000
TARGET_SIZE = (128, 128)
MODEL_PATH = '/home/team46/new_rw_detector_gain.h5'

# Audio processing
WEEVIL_LOWCUT = 93.75
WEEVIL_HIGHCUT = 2500
FILTER_ORDER = 4
GAIN_FACTOR = 1000

# led = LED(17)

def butter_bandpass(lowcut, highcut, sr, order=4):
    nyquist = 0.5 * sr
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, sr, order=4):
    b, a = butter_bandpass(lowcut, highcut, sr, order=order)
    y = lfilter(b, a, data)
    return y

def apply_gain(audio, gain_factor):
    amplified = audio * gain_factor
    return np.clip(amplified, -1.0, 1.0)

def record_audio():
    """Record 15 seconds but keep only last 10 seconds"""
    cmd = [
        'arecord',
        '-d', str(TOTAL_RECORD_TIME),
        '-f', 'S16_LE',
        '-r', str(SAMPLE_RATE),
        '-c', '1',
        '-q',
        '-t', 'wav'
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    audio_data, _ = process.communicate()
    
    # Convert to numpy array and remove WAV header
    full_audio = np.frombuffer(audio_data, dtype=np.int16)[44:] / 32768.0
    
    # Calculate samples to keep (last 10 seconds)
    total_samples = len(full_audio)
    keep_samples = KEEP_LAST_SECONDS * SAMPLE_RATE
    start_index = max(0, total_samples - keep_samples)
    
    # Extract last 10 seconds
    last_10s = full_audio[start_index:]
    
    # Apply processing chain
    filtered = bandpass_filter(
        last_10s,
        lowcut=WEEVIL_LOWCUT,
        highcut=WEEVIL_HIGHCUT,
        sr=SAMPLE_RATE,
        order=FILTER_ORDER
    )
    amplified = apply_gain(filtered, GAIN_FACTOR)
    
    return amplified

def create_spectrogram(audio):
    plt.figure(figsize=(10,4), frameon=False)
    S = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_mels=N_MELS,
        fmax=FMAX,
        fmin=WEEVIL_LOWCUT
    )
    S_dB = librosa.power_to_db(S, ref=np.max)

    librosa.display.specshow(
        S_dB,
        sr=SAMPLE_RATE,
        cmap='viridis',
        x_axis='time',
        y_axis='mel',
        fmax=FMAX
    )
    
    plt.axis('off')
    plt.tight_layout(pad=0)
    
    fig = plt.gcf()
    fig.canvas.draw()
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    plt.close('all')
    return img

def preprocess_image(img_array):
    img_array = tf.image.resize(img_array, TARGET_SIZE)
    img_array = img_array / 255.0
    return np.expand_dims(img_array, axis=0)

def load_model():
    try:
        interpreter = tf.lite.Interpreter(model_path=MODEL_PATH.replace('.h5','.tflite'))
        interpreter.allocate_tensors()
        return interpreter
    except:
        return tf.keras.models.load_model(MODEL_PATH, compile=False)

def predict(model, input_data):
    if isinstance(model, tf.lite.Interpreter):
        input_details = model.get_input_details()
        output_details = model.get_output_details()
        model.set_tensor(input_details[0]['index'], input_data)
        model.invoke()
        return model.get_tensor(output_details[0]['index'])[0][0]
    else:
        return model.predict(input_data, verbose=0)[0][0]


def detect_rice_weevil():
    model = load_model()

    start_total = time.time()
    max_duration = 70  # seconds
    weevil_count = 0
    clean_count = 0

    while True:
        elapsed_total = time.time() - start_total
        if elapsed_total > max_duration:
            # led.off()
            # led.close()
            break

        audio = record_audio()
        spectrogram = create_spectrogram(audio)
        processed_img = preprocess_image(spectrogram)

        confidence = predict(model, processed_img)
        weevil_detected = confidence > 0.5

        if weevil_detected:
            weevil_count += 1
            # led.on()
        else:
            clean_count += 1
            # led.off()

        time.sleep(0.5)

    if weevil_count >= 0:
        return True
    else:
        return False
