import os
from typing import Iterator, Literal
import openai
import pyaudio
import dotenv
import threading
import time
from pathlib import Path

from openai import OpenAI

dotenv.load_dotenv()

# gets OPENAI_API_KEY from your environment variables
openai = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"


def text_to_speech_stream(text: str, voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"):
    with openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        voice=voice,
        input=text,
    ) as response:
        for chunk in response.iter_bytes(chunk_size=1024):
            yield chunk


def stream_to_speakers(player: pyaudio.Stream, text: str):
    start_time = time.time()
    try:
        for chunk in text_to_speech_stream(text):
            player.write(chunk)
    except Exception as e:
        print(e)
    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")


def get_audio_player() -> pyaudio.Stream:
    return pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)


def start_stream(player: pyaudio.Stream, text: str):
    speaker_thread = threading.Thread(
        target=stream_to_speakers,
        args=[player, text],
    )
    speaker_thread.start()
    return speaker_thread


def stop_stream(player: pyaudio.Stream, thread: threading.Thread):
    player.stop_stream()
    thread.join()


def main():
    audio_player = get_audio_player()
    text = """I see skies of blue and clouds of white
                The bright blessed days, the dark sacred nights
                And I think to myself
                What a wonderful world"""
    speaker_thread = start_stream(audio_player, text)
    time.sleep(3)
    stop_stream(audio_player, speaker_thread)


if __name__ == "__main__":
    main()
