import re
import openai
from dotenv import load_dotenv
import os
from ..util.logging import logging
from typing import List, Dict, Any, Tuple

class GPTController:
    def __init__(self) -> None:
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def send_translation_request(self, texts_batch: List[Dict[str, Any]]) -> List[Tuple[int, str]]:
        # Combine texts, each text is between two backticks
        combined_texts: str = "\n".join([f"{text['id']}|`{text['orig']}`" for text in texts_batch])
        logging.info(f"Sending a translation request with {len(texts_batch)} texts.")
        logging.debug(f"Model: {os.getenv('OPENAI_MODEL')}")
        try:
            response: Dict[str, Any] = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL"),
                messages = [
                    {
                        "role": "system", 
                        "content": (
                            "You are an expert RPGMaker game translator specializing in Japanese to English translations."
                            "Your job is to translate texts accurately, with special attention to tone, character, and context. "
                            "When translating, follow these guidelines strictly:\n"
                            "1. **Preserve special characters and formatting** (e.g., \\c[27], \\n, \\V[n], etc.) exactly as they appear. "
                            "These formatting elements are crucial to the game’s mechanics and must remain unchanged.\n"
                            "2. **Translate character names naturally into English** if possible. Do not use literal translations of names.\n"
                            "3. **Use natural, colloquial English** in translations. The language should sound as if it were written by a native English speaker.\n"
                            "4. **Do not censor vulgar or sexual terms**. If a vulgar term appears, translate it directly and use appropriate English term or colloquialism. "
                            "For example, if the Japanese text contains slang or vulgar terms like genitals, 'pussy' would be an appropriate translation for colloquial contexts.\n"
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
            def strip_code_blocks(response: str) -> str:
                """
                Strips any code block markers (e.g., ```plaintext, ```yaml, etc.) 
                from the beginning and end of the response, 
                but leaves them intact if they are in the middle of the string.
                """
                # Pattern to match code block at the beginning (e.g., ```plaintext, ```yaml, etc.)
                start_pattern = r'^```[a-zA-Z]*\n?'
                # Pattern to match code block at the end (e.g., ```)
                end_pattern = r'\n?```$'

                # Remove code block from the beginning if it exists
                response = re.sub(start_pattern, '', response)

                # Remove code block from the end if it exists
                response = re.sub(end_pattern, '', response)

                return response.strip()
                    
            response_text: str = strip_code_blocks(response['choices'][0]['message']['content'])
            translated_texts: List[str] = response_text.split('\n')

            # Log how many texts were received
            logging.info(f"Received {len(translated_texts)} translated texts.")
            logging.debug(f"Translated texts: {translated_texts}")

            # Map translations back to the original texts
            indexed_translations: List[Tuple[int, str]] = []
            for translated_line in translated_texts:
                # Split to capture line numbers and text within backticks
                parsed: List[str] = translated_line.split('|')
                index: int = int(parsed[0])
                text: str = parsed[1].strip('`').strip()
                if text:
                    indexed_translations.append((index, text))

            return indexed_translations

        except Exception as e:
            logging.error(f"Translation request failed: {e}")
            raise e
