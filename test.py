import json
from NaiveTranslator import NaiveTranslator
from SimpleTranslator import SimpleTranslator
from ChatTranslator import ChatTranslator
from SimpleFewShotTranslator import SimpleFewShotTranslator
from SimpleImageTranslator import SimpleImageTranslator
from ImageChatTranslator import ImageChatTranslator
from DescriptionImageTranslator import DescriptionImageTranslator
from SummaryTranslator import SummaryTranslator
from LineTranslator import LineTranslator
from BestTranslator import BestTranslator
from tqdm import tqdm

folder = "open-mantra-dataset/"
annotations = json.load(open(f"{folder}annotation.json"))
translated_books = {}
short_test = True
test_length = 10

# Define translators outside the book loop
translators = {
    "NaiveTranslator": NaiveTranslator(),
    # "BestTranslator": BestTranslator(model="llama3.2-vision:latest"),
    # "BestTranslator": BestTranslator(),
    "BestTranslator-ab": BestTranslator(
        base_url="http://localhost:5001/v1/",
        model="qwen25vl:32b",
        prefix_prompt="Your job is to translate the following text to English. I will show you the full text beforehand, but we will translate it line by line. You will have to reply only with the translated line. Always write just one translation, which is the most fitting.\nJapanese manga text:\n",
    ),
    # "BestTranslator-ab": BestTranslator(base_url="http://localhost:5001/v1/", model="qwen25vl"),
    ##"SimpleTranslator-deepseek-r1:8b": SimpleTranslator(model="deepseek-r1:8b"),
    # "SimpleTranslator": SimpleTranslator(),
    # "SummaryTranslator": SummaryTranslator(),
    # "SummaryTranslator-gemma3:12b": SummaryTranslator(model="gemma3:12b"),
    # "ImageChatTranslator": ImageChatTranslator(),
    # "DescriptionImageTranslator": DescriptionImageTranslator(),
    # "SimpleTranslator-gemma3:12b": SimpleTranslator(model="gemma3:12b"),
    # "SimpleImageTranslator": SimpleImageTranslator(),
    # "SimpleImageTranslator-prompt": SimpleImageTranslator(prefix_prompt="Translate the following text to English. First describe the image, then write the translations for the text in a numbered format. The translation should be only the transalted English text without notes.\nJapanese manga text:\n"),
    # "SimpleImageTranslator-minicpm-v:8b": SimpleImageTranslator(model="minicpm-v:8b"),
    # "SimpleTranslator-minicpm-v:8b": SimpleTranslator(model="minicpm-v:8b"),
    # "SimpleTranslator-qwen2.5:14b": SimpleTranslator(model="qwen2.5:14b"),
    # "ChatTranslator": ChatTranslator(),
    ## "ChatTranslator-limit5": ChatTranslator(limit=5),
    # "ChatTranslator-gemma3:12b": ChatTranslator(model="gemma3:12b"),
    ## "ChatTranslator-minicpm-v:8b": ChatTranslator(model="minicpm-v:8b"),
    # "SimpleFewShotTranslator-gemma3:12b": SimpleFewShotTranslator(model="gemma3:12b"),
    ## "SimpleFewShotTranslator-qwen2.5:14b": SimpleFewShotTranslator(model="qwen2.5:14b"),
    # "SimpleFewShotTranslator-minicpm-v:8b": SimpleFewShotTranslator(
    #     model="minicpm-v:8b"
    # ),
}

# Initialize the translated_books structure first
for book in annotations:
    book_title = book["book_title"]
    translated_books[book_title] = []
    for n, page in enumerate(book["pages"]):
        if n > test_length and short_test:
            print(f"Skipping pages after 5 for {book_title} to save time.")
            break

        image = folder + page["image_paths"]["ja"]
        texts = page["text"]
        ja_text = "\n".join([t["text_ja"] for t in texts])
        en_text = "\n".join([t["text_en"] for t in texts])

        translation_output = {"ja_text": ja_text, "en_text": en_text, "image": image}
        # Initialize with empty translations
        for name in translators.keys():
            translation_output[name] = ""

        translated_books[book_title].append(translation_output)

# Now process each translator across all books
for name, translator in translators.items():
    print(f"Using translator: {name}")
    for book in annotations:
        book_title = book["book_title"]
        print(f"Translating book: {book_title}")
        translator.reset_state()
        for n, page in tqdm(enumerate(book["pages"])):
            if n > test_length and short_test:
                # print(f"Skipping pages after 5 for {book_title} to save time.")
                break

            # print(f"Page {n + 1}/{len(book['pages'])}")
            image = folder + page["image_paths"]["ja"]
            texts = page["text"]
            ja_text = "\n".join([t["text_ja"] for t in texts])

            try:
                translation = translator.translate(ja_text, image)
                translated_books[book_title][n][name] = translation
            except Exception as e:
                print(f"Error in {name} for {book_title}, page {n+1}: {e}")

with open("translated_books.json", "w") as f:
    json.dump(translated_books, f, indent=4, ensure_ascii=False)
print("Translation completed and saved to translated_books.json")
