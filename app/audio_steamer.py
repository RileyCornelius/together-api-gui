from queue import Queue
import shutil
import subprocess
import threading
from typing import Iterator, Literal

from openai import OpenAI


def is_installed(lib_name: str) -> bool:
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True


class AudioStreamer:
    def __init__(self):
        self.is_streaming = False
        self.audio = Queue()
        self.text = Queue()

    def start_streaming(self, stream=None):
        self.is_streaming = True
        self.audio = Queue()
        self.text = Queue()
        threading.Thread(target=self._tts_thread, daemon=True).start()
        threading.Thread(target=self._audio_thread, daemon=True).start()

        if stream:
            for chunk in stream:
                print(chunk, end="", flush=True)
                self.text.put(chunk)

    def stop_streaming(self):
        self.is_streaming = False
        # time.sleep(0.5)

    def _tts_thread(self):
        sentence = ""
        while self.is_streaming:
            chunk = self.text.get()
            sentence += chunk
            # TODO: add a better way to detect end of sentence
            if chunk and chunk[-1] in ".!?":
                audio_stream = self._tts_streaming(sentence)
                self.audio.put(audio_stream)
                sentence = ""

    def _audio_thread(self):
        while self.is_streaming:
            self._audio_streaming(self._stream_audio_generator())

    def _stream_audio_generator(self) -> Iterator[bytes]:
        while self.is_streaming:
            sentence_audio = self.audio.get()
            for bytes in sentence_audio.iter_bytes():
                yield bytes

    def _tts_streaming(
        self,
        text: str,
        voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"] = "echo",
        model: Literal["tts-1", "tts-1-hd"] = "tts-1",
        speed: float = 1.0,
    ):
        client = OpenAI()
        stream = client.audio.speech.create(
            input=text,
            model=model,
            voice=voice,
            response_format="mp3",
            speed=speed,
            stream=True,
        )
        return stream

    def _audio_streaming(self, audio_stream: Iterator[bytes]) -> bytes:
        if not is_installed("mpv"):
            message = (
                "mpv not found, necessary to stream audio. "
                "On mac you can install it with 'brew install mpv'. "
                "On linux and windows you can install it from https://mpv.io/"
            )
            raise ValueError(message)

        mpv_command = ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"]
        mpv_process = subprocess.Popen(
            mpv_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        audio = bytes()
        for chunk in audio_stream:
            if not self.is_streaming:
                mpv_process.terminate()
                break
            if chunk is not None:
                mpv_process.stdin.write(chunk)
                mpv_process.stdin.flush()
                audio += chunk

        if mpv_process.stdin:
            mpv_process.stdin.close()
        mpv_process.wait()

        self.stop_streaming()
        return audio


# def text_chunker(chunks: Iterator[str]) -> Iterator[str]:
#     """Used during input streaming to chunk text blocks and set last char to space"""
#     splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
#     buffer = ""
#     for text in chunks:
#         if buffer.endswith(splitters):
#             yield buffer if buffer.endswith(" ") else buffer + " "
#             buffer = text
#         elif text.startswith(splitters):
#             output = buffer + text[0]
#             yield output if output.endswith(" ") else output + " "
#             buffer = text[1:]
#         else:
#             buffer += text
#     if buffer != "":
#         yield buffer + " "


# mixtral = Mixtral()
# steamer = AudioStreamer()
# prompt = "what are you"
# stream = mixtral.chat_stream(prompt)
# steamer.start_streaming(stream)

# time.sleep(5)
# steamer.stop_streaming()
# print("Stopped")
# time.sleep(2)
# stream = mixtral.chat_stream(prompt)
# steamer.start_streaming(stream)
# print("Started")

# time.sleep(5)
