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
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"
HEADERS = {"Authorization": "Bearer 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"}
SAMPLERATE = 16000  # Set a standard sampling rate for speech recording
recording = False

# Default file names
default_original_filename = "transcription.txt"
default_cleaned_filename = "cleaned_transcription.txt"
default_audio_filename = "recorded_audio.wav"

# Step 1: Start Recording Audio until stopped
def record_audio(selected_device):
    global recording
    audio_data = []
    print("Recording started. Type 'stop' to stop.")
    recording = True
    
    # Recording loop
    while recording:
        chunk = sd.rec(int(SAMPLERATE * 0.5), samplerate=SAMPLERATE, channels=1, dtype=np.int16, device=selected_device)  # Record in chunks of 0.5 seconds
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
def transcribe_audio(audio_data):
    # Save the recorded data as a temporary wav file in memory
    wav_buffer = BytesIO()
    wavfile.write(wav_buffer, SAMPLERATE, audio_data)
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

# Step 5: Save Transcription via File Explorer
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

# Main Process Flow
def main():
    # List available audio input devices
    devices = sd.query_devices()
    print("Available audio input devices:")
    for idx, device in enumerate(devices):
        if device['max_input_channels'] > 0:
            print(f"{idx}: {device['name']}")

    selected_device = int(input("Select an input device by index: "))
    print(f"Selected device: {devices[selected_device]['name']}")

    # Start recording in a separate thread to allow stopping it
    record_thread = threading.Thread(target=stop_recording)
    record_thread.start()

    # Record audio until stopped
    audio_data = record_audio(selected_device)
    record_thread.join()  # Wait for the user to stop recording

    # Save the recorded audio to a file
    wavfile.write(default_audio_filename, SAMPLERATE, audio_data)
    print(f"Audio saved to {default_audio_filename}")

    # Transcribe the recorded audio with retry logic
    transcription = transcribe_audio(audio_data)
    if transcription:
        print("Original Transcription:\n", transcription)

        # Save the original transcription
        save_file(transcription, "Save the original transcription", default_original_filename, [("Text Files", "*.txt")])

        # Remove fillers and save the cleaned transcription
        cleaned_transcription = remove_filler_words(transcription)
        print("Cleaned Transcription:\n", cleaned_transcription)
        save_file(cleaned_transcription, "Save the cleaned transcription", default_cleaned_filename, [("Text Files", "*.txt")])

if __name__ == "__main__":
    main()
