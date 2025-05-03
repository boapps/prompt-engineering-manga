from Translator import Translator
from openai import OpenAI
import re
import base64
from cachier import cachier


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class BestTranslator(Translator):
    def __init__(
        self,
        model="gemma3:12b",
        base_url="http://localhost:11434/v1",
        api_key="ollama",
        system_prompt="You are a professional manga translator and image captioner.",
        prefix_prompt="Your job is to translate the following text to English. I will show you the full text beforehand, but we will translate it line by line. You will have to reply only with the translated line.\nJapanese manga text:\n",
        image_prompt="First just give a short (1-2 paragraph) description of only the visual scene. Focus on the characters and the background. Don't write anything else.",
        new_summary_prompt="Now give a short (1-2 paragraph) but precise summary of the story so far based on the image and text.",
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.prefix_prompt = prefix_prompt
        self.summary = None
        self.image_prompt = image_prompt
        self.new_summary_prompt = new_summary_prompt
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def reset_state(self):
        self.summary = None

    def translate(self, text, image_path):
        summary, translation = self.do_translation(
            text,
            image_path,
            self.summary,
            self.prefix_prompt,
            self.system_prompt,
            self.model,
            self.image_prompt,
            self.new_summary_prompt,
        )
        self.summary = summary
        return translation

    @cachier()
    def do_translation(
        self,
        text,
        image_path,
        summary,
        prefix_prompt,
        system_prompt,
        model,
        image_prompt,
        new_summary_prompt,
    ):
        base64_image = encode_image(image_path)
        input_len = len(text.split("\n"))
        numbered_text = "\n".join(
            [f"{i + 1}: {line}" for i, line in enumerate(text.split("\n"))]
        )
        summary_prompt = (
            ("Summary of the story so far:\n" + summary + "\n") if summary else ""
        )
        prompt = f"{summary_prompt}{prefix_prompt}{numbered_text}\nAre you ready?"
        history = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": image_prompt,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            },
        ]
        print(history)
        completion = self.client.chat.completions.create(
            model=model,
            temperature=0,
            messages=history,
            max_completion_tokens=500,
        )
        print("description")
        print(completion.choices[0].message.content)
        history.append(completion.choices[0].message)
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": "Yes, I am ready."})
        translated_text = []
        for line in text.split("\n"):
            history.append({"role": "user", "content": line})
            completion = self.client.beta.chat.completions.parse(
                model=model,
                temperature=0,
                messages=history,
                max_completion_tokens=500,
            )
            history.append(completion.choices[0].message)
            translated_text.append(completion.choices[0].message.content.strip())
        print("translated_text")
        print(translated_text)
        history.append(
            {
                "role": "user",
                "content": new_summary_prompt,
            }
        )
        completion = self.client.beta.chat.completions.parse(
            model=model,
            temperature=0,
            messages=history,
            max_completion_tokens=500,
        )
        summary = completion.choices[0].message.content
        # print('\n'.join(self.get_number_lines(completion.choices[0].message.content).split('\n')[-input_len:]))
        print("summary")
        print(summary)
        return summary, "\n".join(translated_text)
