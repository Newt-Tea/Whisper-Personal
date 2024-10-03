import openai
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Initialize OpenAI API key (replace with your own API key)
openai.api_key = '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'

# Function to transcribe audio using OpenAI's Whisper API
def transcribe_audio_via_api(file_path: str) -> str:
    try:
        # Open the audio file in binary mode
        with open(file_path, 'rb') as audio_file:
            # Call OpenAI's Whisper API for transcription
            transcription = openai.Audio.transcribe(
                model="whisper-1",  # API model for Whisper transcription
                file=audio_file
            )
            return transcription['text']
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""

# Function to call GPT and process the transcription
def process_transcription_with_gpt(transcription: str) -> str:
    response = openai.Completion.create(
        engine="gpt-4",
        prompt=transcription,
        max_tokens=150  # Adjust as necessary
    )
    return response.choices[0].text.strip()

# Function to get file path using file explorer
def get_audio_file_path() -> str:
    # Hide the root window
    Tk().withdraw()
    # Open the file dialog to select an audio file
    file_path = askopenfilename(
        title="Select an Audio File",
        filetypes=[("Audio Files", "*.mp3 *.mp4 *.mpeg *.mpga *.wav *.webm")]
    )
    return file_path

# Function to save text to a file
def save_to_file(file_name: str, content: str) -> None:
    try:
        with open(file_name, 'w') as f:
            f.write(content)
        print(f"File saved successfully: {file_name}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    # Step 1: Get the audio file path from the user
    audio_file_path = get_audio_file_path()

    if audio_file_path:
        # Step 2: Transcribe audio using OpenAI's Whisper API
        transcription = transcribe_audio_via_api(audio_file_path)
        print("Transcription: ", transcription)
        
        # Save transcription to a file
        transcription_file = "transcription.txt"
        save_to_file(transcription_file, transcription)
        
        # Step 3: Send transcription to GPT for further processing
        gpt_response = process_transcription_with_gpt(transcription)
        print("GPT Response: ", gpt_response)
        
        # Save GPT response to a file
        gpt_file = "gpt_response.txt"
        save_to_file(gpt_file, gpt_response)
    else:
        print("No file selected.")
