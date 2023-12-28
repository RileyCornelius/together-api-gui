import gradio as gr

from audio_streamer import AudioStreamer
from mixtral import Mixtral

MICROPHONE_ICON_URL = "https://cdn-icons-png.flaticon.com/512/25/25682.png"

mixtral = Mixtral()
audio_streamer = AudioStreamer()


def user_chat(input_text: str, chat_history: list):
    chat_history.append([input_text, None])
    return "", chat_history


def respond(chat_history: list):
    chat_history[-1][1] = ""
    prompt = chat_history[-1][0]
    stream = mixtral.chat_stream(prompt)
    for chunk in stream:
        chat_history[-1][1] += chunk
        yield chat_history


def respond_audio(chat_history: list):
    if audio_streamer.is_streaming:
        audio_streamer.stop_streaming()

    audio_path = audio_streamer.listening()
    prompt = audio_streamer.speech_to_text_whisper(audio_path)

    chat_history.append([prompt, ""])

    stream = mixtral.chat_stream(prompt)
    audio_streamer.start_streaming()
    for chunk in stream:
        audio_streamer.text.put(chunk)
        chat_history[-1][1] += chunk
        yield chat_history


with gr.Blocks() as demo:
    with gr.Tab(label="Mixtral Chat"):
        gr.HTML(value="<center><h1>Mixtral Chat</h1></center>")
        chatbot = gr.Chatbot(height=600, bubble_full_width=True)
        with gr.Row():
            textbox = gr.Textbox(placeholder="Type here to chat.")
            audio_button = gr.Button(value="", scale=0.1, icon=MICROPHONE_ICON_URL)

        with gr.Row():
            clear_button = gr.ClearButton([textbox, chatbot]).click(
                fn=lambda: mixtral.clear_history()
            )
            stop_button = gr.Button(value="Stop Audio").click(
                fn=lambda: audio_streamer.stop_streaming()
            )

        audio_button.click(fn=respond_audio, inputs=[chatbot], outputs=[chatbot])
        textbox.submit(
            fn=user_chat, inputs=[textbox, chatbot], outputs=[textbox, chatbot]
        ).then(fn=respond, inputs=[chatbot], outputs=[chatbot])

    with gr.Tab(label="Settings"):
        gr.HTML(value="<center><h1>Mixtral Settings</h1></center>")
        gr.Slider(label="Max Tokens", value=512, minimum=512, maximum=2048)


demo.launch(inbrowser=True)
