import sounddevice as sd
import numpy as np
import requests
import re
import tkinter as tk
from tkinter import filedialog
import threading
import time
from io import BytesIO
import scipy.io.wavfile as wavfile

# Constants
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
HEADERS = {"Authorization": "Bearer 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"}
DEFAULT_SAMPLERATE = 16000  # Fallback sample rate
recording = False

# Default file names
default_original_filename = "transcription.txt"
default_cleaned_filename = "cleaned_transcription.txt"
default_audio_filename = "recorded_audio.wav"

# Step 0: Find all inputs at 44.1 kHz or 22.05 kHz
def get_input_devices():
    devices = sd.query_devices()
    available_devices_44100 = []
    available_devices_22050 = []

    for i, device in enumerate(devices):
        if device['max_input_channels'] > 0 and device['default_samplerate'] == 44100:
            available_devices_44100.append((i, device['name']))
        elif device['max_input_channels'] > 0 and device['default_samplerate'] == 22050:
            available_devices_22050.append((i, device['name']))

    return available_devices_44100 if available_devices_44100 else available_devices_22050

# Step 1: Start Recording Audio until stopped
def record_audio(selected_device, samplerate):
    global recording
    audio_data = []
    print("Recording started. Type 'stop' to stop.")
    recording = True
    
    while recording:
        chunk = sd.rec(int(samplerate * 30), samplerate=samplerate, channels=1, dtype=np.int16, device=selected_device)
        sd.wait()
        audio_data.append(chunk)
    
    return np.concatenate(audio_data, axis=0)

# Step 2: Prompt to Confirm Stop Recording
def stop_recording():
    global recording
    while True:
        user_input = input("Type 'stop' to stop recording: ").strip().lower()
        if user_input == 'stop':
            confirm = input("Are you sure you want to stop recording? Type 'yes' to confirm: ").strip().lower()
            if confirm == 'yes':
                recording = False
                break

# Step 3: Transcribe Audio with Retry Logic if Model is Loading
def transcribe_audio(audio_data, samplerate):
    wav_buffer = BytesIO()
    wavfile.write(wav_buffer, samplerate, audio_data)
    wav_buffer.seek(0)
    
    max_retries = 5
    retry_count = 0
    wait_time = 60  # Wait time between retries in seconds
    
    print("Transcribing... This may take a while.")
    while retry_count < max_retries:
        response = requests.post(API_URL, headers=HEADERS, data=wav_buffer)
        if response.status_code == 200:
            return response.json()["text"]
        elif response.status_code == 503:
            print(f"Model is still loading. Retrying in {wait_time} seconds... (Attempt {retry_count + 1} of {max_retries})")
            time.sleep(wait_time)
            retry_count += 1
        else:
            print(f"Error in transcription (status code {response.status_code}):", response.text)
            return None
    
    print("Failed to transcribe after multiple attempts. Try again later.")
    return None

# Step 4: Remove Filler Words from Transcription
def remove_filler_words(transcription):
    fillers = ["uh", "um", "like", "you know", "so", "actually", "basically", "I mean"]
    filler_pattern = re.compile(r'\b(?:' + '|'.join(fillers) + r')\b', re.IGNORECASE)
    cleaned_text = filler_pattern.sub("", transcription)
    return cleaned_text

# Step 5: Save Files via File Explorer
def save_file(content, dialog_title, default_filename, filetypes):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.asksaveasfilename(title=dialog_title, defaultextension=".txt", initialfile=default_filename, filetypes=filetypes)
    if file_path:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"File saved to {file_path}")
    else:
        print("Save operation canceled.")

# Step 6: Save Recorded Audio
def save_audio(audio_data, samplerate):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    audio_file_path = filedialog.asksaveasfilename(title="Save Recorded Audio", defaultextension=".wav", initialfile=default_audio_filename, filetypes=[("WAV files", "*.wav")])
    if audio_file_path:
        wavfile.write(audio_file_path, samplerate, audio_data)
        print(f"Audio saved to {audio_file_path}")
    else:
        print("Audio save operation canceled.")

# Step 7: Get Supported Sample Rates for Selected Device
def get_supported_samplerate(device):
    supported_samplerates = []
    if device['default_samplerate'] >= 44100:
        supported_samplerates.append(44100)
    if device['default_samplerate'] >= 22050:
        supported_samplerates.append(22050)
    supported_samplerates.append(int(device['default_samplerate']))
    
    return supported_samplerates

# Step 8: Display Sample Rate Menu
def display_sample_rate_menu(supported_samplerates):
    print("Choose a sample rate from the supported options:")
    for idx, rate in enumerate(supported_samplerates):
        print(f"{idx + 1}: {rate} Hz")
    
    while True:
        try:
            selected_index = int(input("Enter the number corresponding to the sample rate you want to use: ")) - 1
            if 0 <= selected_index < len(supported_samplerates):
                return supported_samplerates[selected_index]
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

# Load Model Function
def load_model():
    print("Loading the model... This may take a moment.")
    time.sleep(5)  # Simulating a delay for loading the model
    print("Model loaded successfully.")

# Main Process Flow
def main():
    model_thread = threading.Thread(target=load_model)
    model_thread.start()

    input_devices = get_input_devices()
    
    if not input_devices:
        print("No suitable audio input devices found.")
        return

    print("Available audio input devices:")
    for index, name in input_devices:
        print(f"{index}: {name}")
    
    selected_device_index = int(input("Select an input device by index: "))
    print(f"Selected device: {input_devices[selected_device_index][1]}")

    selected_device = sd.query_devices(input_devices[selected_device_index][0])
    supported_samplerates = get_supported_samplerate(selected_device)
    selected_samplerate = display_sample_rate_menu(supported_samplerates)

    print("Recording started. Type 'stop' to stop.")
    
    stop_thread = threading.Thread(target=stop_recording)
    stop_thread.start()

    audio_data = record_audio(input_devices[selected_device_index][0], selected_samplerate)
    model_thread.join()
    print("Model loaded successfully.")
    stop_thread.join()

    save_audio(audio_data, selected_samplerate)

    transcription = transcribe_audio(audio_data, selected_samplerate)

    if transcription:
        cleaned_transcription = remove_filler_words(transcription)
        save_file(transcription, "Save Original Transcription", default_original_filename, [("Text Files", "*.txt")])
        save_file(cleaned_transcription, "Save Cleaned Transcription", default_cleaned_filename, [("Text Files", "*.txt")])
        print("Transcriptions saved successfully.")
    else:
        print("Transcription failed.")

if __name__ == "__main__":
    main()
