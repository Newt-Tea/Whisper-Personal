import requests
import re
import tkinter as tk
from tkinter import filedialog
from io import BytesIO
import scipy.io.wavfile as wavfile

# Constants
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo"
HEADERS = {"Authorization": "Bearer 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"}

# Step 1: Transcribe Audio
def transcribe_audio(file_path):
    wav_buffer = BytesIO()
    samplerate, audio_data = wavfile.read(file_path)
    wavfile.write(wav_buffer, samplerate, audio_data)
    wav_buffer.seek(0)

    response = requests.post(API_URL, headers=HEADERS, data=wav_buffer)
    if response.status_code == 200:
        return response.json()["text"]
    else:
        print(f"Error in transcription (status code {response.status_code}):", response.text)
        return None

# Step 2: Remove Filler Words from Transcription
def remove_filler_words(transcription):
    fillers = ["uh", "um", "like", "you know", "so", "actually", "basically", "I mean"]
    filler_pattern = re.compile(r'\b(?:' + '|'.join(fillers) + r')\b', re.IGNORECASE)
    cleaned_text = filler_pattern.sub("", transcription)
    return cleaned_text

# Step 3: Save File
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
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    audio_file_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("WAV files", "*.wav")])
    
    if audio_file_path:
        transcription = transcribe_audio(audio_file_path)
        if transcription:
            cleaned_transcription = remove_filler_words(transcription)
            save_file(transcription, "Save Original Transcription", "transcription.txt", [("Text Files", "*.txt")])
            save_file(cleaned_transcription, "Save Cleaned Transcription", "cleaned_transcription.txt", [("Text Files", "*.txt")])
            print("Transcriptions saved successfully.")
        else:
            print("Transcription failed.")
    else:
        print("No audio file selected.")

if __name__ == "__main__":
    main()
