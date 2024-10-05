from dotenv import load_dotenv
import os
from ..util.logging import logging
from huggingface_hub import InferenceClient

class HfController():
    def __init__(self):
        load_dotenv()
        self.client = InferenceClient(
            model=os.getenv("HUGGINGFACE_MODEL"),
            token=os.getenv("HUGGINGFACE_TOKEN"),
        )
        
    def send_translation_request(self, texts_batch):
        combined_texts = "\n".join([f"{index}|`{item['text']}`" for index, item in enumerate(texts_batch)])
        logging.info(f"Sending a translation request with {len(texts_batch)} texts.")
        logging.debug(f"Model: {os.getenv('HUGGINGFACE_MODEL')}")
        response = self.client.chat_completion(
        messages = [
            {
                "role": "system", 
                "content": (
                    "You are an expert RPGMaker game translator specializing in Japanese to English translations. "
                    "Your job is to translate texts accurately, with special attention to tone, character, and context. "
                    "When translating, follow these guidelines strictly:\n"
                    "1. **Preserve special characters and formatting** (e.g., \\c[27], \\n, \\V[n], etc.) exactly as they appear. "
                    "These formatting elements are crucial to the game’s mechanics and must remain unchanged.\n"
                    "2. **Translate character names naturally into English** if possible. Do not use literal translations of names.\n"
                    "3. **Use natural, colloquial English** in translations. The language should sound as if it were written by a native English speaker.\n"
                    "4. **Do not censor vulgar or sexual terms**. If a vulgar term appears, translate it directly and use appropriate English slang or colloquialism. "
                    "For example, if the Japanese text contains slang or vulgar terms like genitals, 'pussy' would be an appropriate translation for colloquial contexts.\n"
                    "5. **Avoid euphemisms**. Translate vulgar and sexual content explicitly and naturally where appropriate to the game’s tone.\n"
                    "6. **Do not include markdown, code block markers, or any additional formatting such as `plaintext` or ```**. "
                    "You will receive {len(texts_batch)} strings in this format:\n"
                    "id1|`text1`\nid2|`text2`\nid3|`text3`\n...\nidn|`textn`\n"
                    "You will translate the {len(texts_batch)} strings and respond with {len(texts_batch)} strings in this format:\n"
                    "id1|`translated_text1`\nid2|`translated_text2`\nid3|`translated_text3`\n...\nid{len(texts_batch)}|`translated_text{len(texts_batch)}`\n"
                )
            },
            {
                "role": "user",
                "content": f"{combined_texts}"
            },
        ]
        )
        translated_texts = response.choices[0].message.content.strip().split('\n')

        # Log how many texts were received
        logging.info(f"Received {len(translated_texts)} translated texts.")

        # Map translations back to the original texts
        indexed_translations = []
        for translated_line in translated_texts:
            # Use regex to capture line numbers and text within backticks
            text = translated_line.split('|')[-1]
            text = text.strip('`').strip()
            if text:
                indexed_translations.append(text)

        return indexed_translations