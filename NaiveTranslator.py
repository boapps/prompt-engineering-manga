from Translator import Translator

class NaiveTranslator(Translator):
    def __init__(self):
        super().__init__()

    def translate(self, text, image_path):
        return text
