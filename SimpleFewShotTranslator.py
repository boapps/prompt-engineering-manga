from Translator import Translator
from openai import OpenAI
import re


class SimpleFewShotTranslator(Translator):
    def __init__(
        self,
        model="llama3.1:8b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        system_prompt="You are a professional manga translator. You will be given a comic's text in Japanese. Translate it to English.",
        prefix_prompt="Translate the following text to English. The translation should be only the transalted English text (numbered) without notes.\nJapanese manga text:\n",
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
        numbered_text = "\n".join(
            [f"{i + 1}: {line}" for i, line in enumerate(text.split("\n"))]
        )
        prompt = f"{self.prefix_prompt}{numbered_text}"
        example_prompt = "Translate the following text to English. The translation should be only the transalted English text (numbered) without notes.\nJapanese manga text:\n1. 夢の翼は\n2. 蝋で固めてある\n3. 高く翔ぶほど\n4. 太陽に溶かされてしまう\n5. ーだったら\n6. 最初から翔ばない方がいい"
        example_completion = "1. the wings of dreams,\n2. were coated with wax.\n3. as it flys higher,\n4. it'll melt by the sun.\n5. ...if so\n6. why fly in the first place."
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": example_prompt},
                {"role": "assistant", "content": example_completion},
                {"role": "user", "content": prompt},
            ],
        )
        return self.get_number_lines(completion.choices[0].message.content)
