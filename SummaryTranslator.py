from Translator import Translator
from openai import OpenAI
import re


class SummaryTranslator(Translator):
    def __init__(
        self,
        model="llama3.1:8b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        system_prompt="You are a professional manga translator. You will be given a comic's text in Japanese. Translate it to English.",
        prefix_prompt="Translate the following text to English. The translation should be only the transalted English text (numbered) without notes.\nJapanese manga text:\n",
        limit=None,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.prefix_prompt = prefix_prompt
        self.limit = limit
        self.summary = None
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def reset_state(self):
        self.summary = None

    def get_number_lines(self, text):
        pattern = r"^\d+[\.:]\s*(.*)"
        lines = text.split("\n")
        result = []

        for line in lines:
            match = re.match(pattern, line)
            if match:
                result.append(match.group(1))

        return "\n".join(result)

    def translate(self, text, image_path):
        numbered_text = "\n".join(
            [f"{i + 1}: {line}" for i, line in enumerate(text.split("\n"))]
        )
        summary_prompt = ("Summary of the story so far:\n"+self.summary+"\n") if self.summary else ""
        prompt = f"{summary_prompt}{self.prefix_prompt}{numbered_text}"
        history = [{"role": "user", "content": prompt}]
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=0,
            messages=history,
        )
        history.append(completion.choices[0].message)
        result = self.get_number_lines(completion.choices[0].message.content)
        history.append({"role": "user", "content": "Now give a summary of the story so far."})
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=0,
            messages=history,
        )
        self.summary = completion.choices[0].message.content
        print(self.summary)
        return result
