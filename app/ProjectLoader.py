import os
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from .util.logging import logging

def get_text_from_project(path: str) -> List[Dict[str, Any]]:
    # Crawl from directory/data
    def extract_text(json_files: List[str]) -> List[Dict[str, Any]]:
        """
        Extracts texts from JSON files in the given list of file paths.
        
        :param json_files: A list of file paths to JSON files.
        """
        results: List[Dict[str, Any]] = []

        # Function to extract texts from JSON data
        # It will recursively search for texts in the JSON data
        def find_texts(data: Any, path: str = '', ref: Optional[Tuple[Any, Any]] = None, texts_to_translate: Optional[List[Dict[str, Any]]] = None) -> None:
            if isinstance(data, dict):
                for key, value in data.items():
                    new_path = f"{path}/{key}" if path else key
                    # Recursively find texts in nested dictionaries
                    find_texts(value, new_path, ref=(data, key), texts_to_translate=texts_to_translate)
            elif isinstance(data, list):
                for index, item in enumerate(data):
                    new_path = f"{path}[{index}]"
                    # Recursively find texts in nested lists
                    find_texts(item, new_path, ref=(data, index), texts_to_translate=texts_to_translate)
            elif isinstance(data, str):
                # Only append text to 'texts_to_translate' if the key is in the specified keys
                key = re.sub(r'\[\d+\]', '', path.split('/')[-1]) # Remove array index from key
                if ref and contains_japanese(data):
                    if texts_to_translate is not None:
                        texts_to_translate.append({'path': path, 'text': data, 'ref': ref, 'key': key})


                
        # Function to check if a string contains Japanese characters
        # Specifically, it checks for Hiragana, Katakana, Kanji, and punctuation/symbols
        def contains_japanese(text: str) -> bool:
            japanese_regex = re.compile(
                r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u3000-\u303F]'
            )
            return bool(japanese_regex.search(text))

        for json_file in json_files:
            texts_to_translate: List[Dict[str, Any]] = []  # Create a new list for each file
            with open(json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                find_texts(data, texts_to_translate=texts_to_translate)  # Correctly pass the list
                json_texts: Dict[str, Any] = {
                    'json_file': json_file,  # File path
                    'num_texts': len(texts_to_translate),  # Number of texts to translate
                    'num_translated': 0,  # Number of texts already translated
                    'texts': [{'id': index, 'ref': text['ref'], 'orig': text['text'], 'trans': '', 'key': text['key'], 'path': text['path']} for index, text in enumerate(texts_to_translate)],
                    'data': data  # Original JSON data
                }
                results.append(json_texts)

        return results

    def crawl(path: str) -> List[str]:
        """
        Grabs all the JSON files in the given path and its subdirectories.
        
        :param path: The path to the directory to crawl.
        """
        # Check if the path is valid
        if not os.path.exists(path):
            print("Invalid path. Please try again.")
            return []
        
        # Crawl the directory, grab all the JSON files
        json_files: List[str] = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".json"):
                    json_files.append(os.path.join(root, file))
        
        # Return the list of JSON files
        return json_files
    
    json_files = crawl(os.path.join(path, 'www', 'data')) # Change this to whatever path your rpg maker version uses
    return extract_text(json_files)

def apply_translations_to_project(json_file_data: List[Dict[str, Any]]) -> None:
    """
    Applies translations to the project by updating the original JSON files with translated text.

    :param json_file_data: A list of dictionaries with JSON file information, text to translate, and references.
                           This should be in the same format as returned by `get_text_from_project`.
    """
    for file_data in json_file_data:
        json_file_path = file_data['json_file']  # Path to the original JSON file
        original_data = file_data['data']        # Original JSON data
        texts = file_data['texts']               # List of texts with 'id', 'ref', 'orig', and 'trans'

        logging.info(f"Applying translations to {json_file_path}...")
        # Update the JSON data based on the translations
        for text_info in texts:
            ref = text_info['ref']  # Reference to the location in the original data
            translated_text = text_info['trans']  # Translated text

            # Add debug for the original value before translation
            original_value = ref[0][ref[1]] if ref and ref[0] else None
            logging.info(f"Original value: {original_value}, Translated: {translated_text}, Skipping: {not ref or not translated_text}")

            # If ref is valid, apply the translated text
            if ref and translated_text:
                update_json_data(ref, translated_text)

        # Write the updated data back to the original file
        with open(json_file_path, 'w', encoding='utf-8') as json_file:
            json.dump(original_data, json_file, ensure_ascii=False, separators=(',', ':'))
            logging.info(f"Translations applied to {json_file_path}")


def update_json_data(ref: Any, translated_text: str) -> None:
    """
    Updates the JSON data at the given reference with the translated text.

    :param ref: A tuple containing a reference to a list or dict in the original JSON data.
    :param translated_text: The translated text to be inserted at the reference.
    """
    parent, key_or_index = ref

    # Ensure we're dealing with the correct parent and key_or_index
    if isinstance(parent, dict):
        original_text = parent.get(key_or_index, "")
        logging.info(f"Updating dict key '{key_or_index}' from '{original_text}' to '{translated_text}'")
        parent[key_or_index] = translated_text

    elif isinstance(parent, list):
        if key_or_index < len(parent):
            original_text = parent[key_or_index]
            logging.info(f"Updating list index {key_or_index} from '{original_text}' to '{translated_text}'")
            parent[key_or_index] = translated_text
        else:
            logging.error(f"List index {key_or_index} is out of bounds")
