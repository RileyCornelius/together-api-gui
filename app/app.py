import gradio as gr

from audio_streamer import AudioStreamer
from mistral import Mistral

MICROPHONE_ICON_URL = "https://cdn-icons-png.flaticon.com/512/25/25682.png"

mistral = Mistral()
audio_streamer = AudioStreamer()


def user_chat(input_text: str, chat_history: list):
    chat_history.append([input_text, None])
    return "", chat_history


def respond(chat_history: list):
    chat_history[-1][1] = ""
    prompt = chat_history[-1][0]
    stream = mistral.chat_stream(prompt)
    for chunk in stream:
        chat_history[-1][1] += chunk
        yield chat_history


def respond_audio(chat_history: list):
    if audio_streamer.is_streaming:
        audio_streamer.stop_streaming()

    audio_path = audio_streamer.listening()
    prompt = audio_streamer.speech_to_text_whisper(audio_path)

    chat_history.append([prompt, ""])

    stream = mistral.chat_stream(prompt)
    audio_streamer.start_streaming()
    for chunk in stream:
        audio_streamer.text.put(chunk)
        chat_history[-1][1] += chunk
        yield chat_history


with gr.Blocks() as demo:
    with gr.Tab(label="Mistral Chat"):
        gr.HTML(value="<center><h1>Mistral Chat</h1></center>")
        chatbot = gr.Chatbot(height=600, bubble_full_width=True)
        with gr.Row():
            textbox = gr.Textbox(placeholder="Type here to chat.")
            audio_button = gr.Button(value="", scale=0.1, icon=MICROPHONE_ICON_URL)

        with gr.Row():
            clear_button = gr.ClearButton([textbox, chatbot]).click(fn=lambda: mistral.clear_history())
            stop_button = gr.Button(value="Stop Audio").click(fn=lambda: audio_streamer.stop_streaming())

        audio_button.click(fn=respond_audio, inputs=[chatbot], outputs=[chatbot])
        textbox.submit(fn=user_chat, inputs=[textbox, chatbot], outputs=[textbox, chatbot]).then(fn=respond, inputs=[chatbot], outputs=[chatbot])

    with gr.Tab(label="Settings"):
        gr.HTML(value="<center><h1>Mistral Settings</h1></center>")
        MISTRAL_CHOICES = ["mistralai/Mixtral-8x7B-Instruct-v0.1", "mistralai/Mistral-7B-Instruct-v0.2", "mistralai/Mistral-7B-Instruct-v0.1"]
        mistral_model_dropdown = gr.Dropdown(label="Mistral Model", value="mistralai/Mixtral-8x7B-Instruct-v0.1", choices=MISTRAL_CHOICES)
        max_tokens = gr.Slider(label="Max Tokens", value=512, minimum=1, maximum=32768)
        temperature = gr.Slider(label="Temperature", value=0.7, minimum=0.0, maximum=2.0)
        top_p = gr.Slider(label="Top P", value=0.7, minimum=0.0, maximum=1.0)
        top_k = gr.Slider(label="Top K", value=50, minimum=1, maximum=100)
        repetition_penalty = gr.Slider(label="Repetition Penalty", value=1.0, minimum=1.0, maximum=2.0)

        mistral_model_dropdown.select(fn=lambda value: setattr(mistral, "model", value), inputs=[mistral_model_dropdown])
        max_tokens.release(fn=lambda value: setattr(mistral, "max_tokens", value), inputs=[max_tokens])
        temperature.release(fn=lambda value: setattr(mistral, "temperature", value), inputs=[temperature])
        top_p.release(fn=lambda value: setattr(mistral, "top_p", value), inputs=[top_p])
        top_k.release(fn=lambda value: setattr(mistral, "top_k", value), inputs=[top_k])
        repetition_penalty.release(fn=lambda value: setattr(mistral, "repetition_penalty", value), inputs=[repetition_penalty])

        # gr.HTML(value="<center><h1>TTS Settings</h1></center>")
        # voice_dropdown = gr.Dropdown(
        #     label="Voice",
        #     value="echo",
        #     choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        # )
        # model_dropdown = gr.Dropdown(
        #     label="Model", value="tts-1-hd", choices=["tts-1", "tts-1-hd"]
        # )

        # voice_dropdown.select(
        #     fn=lambda value: setattr(mixtral, "voice", value), inputs=[voice_dropdown]
        # )


demo.launch(inbrowser=True)
