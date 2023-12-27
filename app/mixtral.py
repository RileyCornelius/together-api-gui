import os
import together
import dotenv

dotenv.load_dotenv()
together.api_key = os.getenv("TOGETHER_API_KEY")


class Mixtral:
    def __init__(self):
        self.max_tokens = 512
        self.temperature = 0.7
        self.top_k = 50
        self.top_p = 0.7
        self.repetition_penalty = 1

        self._model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
        self._stop = ["</s>"]
        self._history = []

    def chat(self, text: str):
        prompt = self._build_prompt(text)
        output = together.Complete.create(
            prompt=prompt,
            model=self._model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            repetition_penalty=self.repetition_penalty,
            cast=True,
            stop=self._stop,
        )

        text = output.choices[0].text
        self._append_history(text, output.choices[0].text)
        return text

    def chat_stream(self, text: str):
        prompt = self._build_prompt(text)
        stream = together.Complete.create_streaming(
            prompt=prompt,
            model=self._model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_k=self.top_k,
            top_p=self.top_p,
            repetition_penalty=self.repetition_penalty,
            stop=self._stop,
        )

        output = ""
        for token in stream:
            output += token
            yield token

        self._append_history(text, output)

    def clear_history(self):
        self._history = []

    def _build_prompt(self, user_input: str):
        """
        <s> [INST] Instruction [/INST] Model answer</s> [INST] Follow-up instruction [/INST]
        """
        prompt = "<s>"
        for pair in self._history:
            prompt += " [INST] " + pair[0] + " [/INST] " + pair[1] + "</s> "
        prompt += " [INST] " + user_input + " [/INST]"
        return prompt

    def _append_history(self, user_input: str, model_output: str):
        self._history.append((user_input, model_output))
        return self._history


# text = "hi who are you?"

# llm = Mixtral()
# answer = llm.chat(text)
# print(answer)

# stream = llm.chat_stream("tell me more")
# for token in stream:
#     print(token, end="", flush=True)
