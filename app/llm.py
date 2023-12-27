import os
import json
import requests
import sseclient

import together
import dotenv

dotenv.load_dotenv()
together.api_key = os.getenv("TOGETHER_API_KEY")

model_list = together.Models.list()
print(f"{len(model_list)} models available")
model_names = [model_dict["name"] for model_dict in model_list]
for name in model_names:
    print(name)


history_pairs = []

model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
url = "https://api.together.xyz/inference"

prompt_text = "hi who are you?"


def build_prompt(history_pairs: list, user_input: str):
    prompt = "<s>"
    for pair in history_pairs:
        prompt += " [INST] " + pair[0] + " [/INST] " + pair[1] + "</s> "
    prompt += " [INST] " + user_input + " [/INST]"
    return prompt


def add_pair(history_pairs: list, user_input: str, model_out: str):
    history_pairs.append((user_input, model_out))
    return history_pairs


prompt = build_prompt(history_pairs, prompt_text)

# Normal API

output = together.Complete.create(
    prompt=prompt,
    model=model,
    max_tokens=64,
    temperature=0.7,
    top_k=50,
    top_p=0.7,
    repetition_penalty=1,
    cast=True,
    stop=["</s>"],
)

text = output.choices[0].text
print(text)

# Streaming API

stream = together.Complete.create_streaming(
    prompt=prompt,
    model=model,
    max_tokens=64,
    temperature=0.7,
    top_k=50,
    top_p=0.7,
    repetition_penalty=1,
    stop=["</s>"],
)

for token in stream:
    print(token, end="", flush=True)
