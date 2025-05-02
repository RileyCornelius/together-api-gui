import os
from typing import Iterator, Literal
import openai
import pyaudio
import dotenv
import threading

dotenv.load_dotenv()

import time
from pathlib import Path

from openai import OpenAI

# gets OPENAI_API_KEY from your environment variables
# openai = OpenAI()

speech_file_path = Path(__file__).parent / "speech.mp3"


def text_to_speech(client: OpenAI, text: str, voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "alloy"):
    response = openai.audio.speech.with_streaming_response.create(
        model="tts-1",
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input=text,
        voice=voice,
    )
    return response


def stream_to_speakers(client: OpenAI, player: pyaudio.Stream, text: str):
    start_time = time.time()
    try:
        response = text_to_speech(client, text)
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        for chunk in response.iter_bytes(chunk_size=1024):
            player.write(chunk)
    except Exception as e:
        print(e)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")


def main():
    stream_player = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)
    openai_client = openai.OpenAI()
    speaker_thread = threading.Thread(
        target=stream_to_speakers,
        args=[
            openai_client,
            stream_player,
            """I see skies of blue and clouds of white
                The bright blessed days, the dark sacred nights
                And I think to myself
                What a wonderful world""",
        ],
    )
    speaker_thread.start()

    time.sleep(2)
    stream_player.stop_stream()
    speaker_thread.join()


if __name__ == "__main__":
    main()
