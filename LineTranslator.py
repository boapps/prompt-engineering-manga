from Translator import Translator
from openai import OpenAI
import re


class LineTranslator(Translator):
    def __init__(
        self,
        model="llama3.1:8b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        system_prompt="You are a professional manga translator. You will be given a comic's text in Japanese. Translate it to English.",
        prefix_prompt="Your job is to translate the following text to English. I will show you the full text beforehand, but we will translate it line by line. You must reply only with the translated line.\nJapanese manga text:\n",
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.prefix_prompt = prefix_prompt
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

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
        input_len = len(text.split("\n"))
        numbered_text = "\n".join(
            [f"{i + 1}: {line}" for i, line in enumerate(text.split("\n"))]
        )
        prompt = f"{self.prefix_prompt}{numbered_text}\nAre you ready?"
        history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": "Yes, I am ready."},
        ]
        translated_text = []
        for line in text.split("\n"):
            history.append({"role": "user", "content": line})
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                temperature=0,
                messages=history,
            )
            history.append(completion.choices[0].message)
            translated_text.append(completion.choices[0].message.content.strip())
        # print('\n'.join(self.get_number_lines(completion.choices[0].message.content).split('\n')[-input_len:]))
        return "\n".join(translated_text)
