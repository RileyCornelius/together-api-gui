import os
from typing_extensions import Union, Literal

from openai import OpenAI
import dotenv
import speech_recognition as sr

dotenv.load_dotenv()


def speech_to_text_whisper(
    audio_file: str,
):
    try:
        client = OpenAI()
        audio_file = open(audio_file, "rb")
        text = client.audio.transcriptions.create(
            file=audio_file, model="whisper-1", response_format="text"
        )
        return text
    except Exception as error:
        print(f"Speech to text error: {error}")
        return ""


def listening():
    try:
        with sr.Microphone() as microphone:
            audio = sr.Recognizer().listen(microphone)
            audio_path = save_audio(audio.get_wav_data(), "cache")
        return audio_path
    except sr.UnknownValueError:
        print("Error: Could not understand audio")
        return ""


def save_audio(data: bytes, file_name: str):
    AUDIO_SAVED_DIRECTORY = "audio/"
    file_name_mp3 = f"{file_name}.wav"
    os.makedirs(AUDIO_SAVED_DIRECTORY, exist_ok=True)
    path = os.path.join(AUDIO_SAVED_DIRECTORY, file_name_mp3)
    with open(path, "wb") as f:
        f.write(data)
    return path
