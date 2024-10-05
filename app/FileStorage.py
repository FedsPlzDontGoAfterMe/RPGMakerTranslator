import json
import os
from typing import List, Dict, Any, Tuple
import re
# Saves all of json_file_data to a file
def save_data(json_file_data: List[Dict[str, Any]], parent_dir: str) -> None:
    """
    Saves the given json_file_data to a file named 'translation_tkinter.json' in the specified parent directory.

    :param json_file_data: A list of dictionaries representing the JSON file data to save.
    :param parent_dir: The parent directory where the file should be saved.
    """
    # Ensure the directory exists
    if not os.path.exists(parent_dir):
        os.makedirs(parent_dir)

    # Define the file path
    file_path = os.path.join(parent_dir, "translation_tkinter.json")

    # Write the JSON data to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(json_file_data, file, ensure_ascii=False, indent=4)

# Loads the json_file_data from a file
def load_data(parent_dir: str) -> List[Dict[str, Any]]:
    """
    Loads the json_file_data from a file named 'translation_tkinter.json' in the specified parent directory.
    After loading, it will reconstruct references to the original JSON data structure.
    
    :param parent_dir: The parent directory from where the data should be loaded.
    :return: A list of dictionaries representing the JSON file data, or an empty list if the file doesn't exist.
    """
    # Define the file path
    file_path = os.path.join(parent_dir, "translation_tkinter.json")

    # Check if the file exists
    if not os.path.exists(file_path):
        return []

    # Load the data from the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Rebuild the references in the data
    reconstruct_references(data)

    return data


def reconstruct_references(data: List[Dict[str, Any]]) -> None:
    """
    Reconstructs references in the loaded data from translation_tkinter.json.
    This is necessary because the original in-memory references are lost after saving/loading.
    
    :param data: The loaded data from translation_tkinter.json.
    """
    for file_data in data:
        original_data = file_data['data']  # This is the original JSON data structure
        for text_info in file_data['texts']:
            path = text_info['path']
            ref = reconstruct_ref_from_path(original_data, path)
            text_info['ref'] = ref  # Rebuild the ref to point to the correct element in original data


def reconstruct_ref_from_path(data: Any, path: str) -> Tuple[Any, Any]:
    """
    Reconstructs the reference to the original data by following the path string.
    
    :param data: The original JSON data structure.
    :param path: The path string used to locate the text in the JSON structure.
    :return: A tuple of (parent, key_or_index) that represents the reference.
    """
    keys = re.split(r'/|\[|\]', path)  # Split by '/' or '[', remove empty strings
    keys = [key for key in keys if key]  # Filter out empty keys caused by splitting

    parent = data
    for key in keys[:-1]:  # Traverse all parts of the path except the last one
        if key.isdigit():  # If key is a digit, it's a list index
            key = int(key)
            parent = parent[key]
        elif isinstance(parent, dict):
            parent = parent.get(key)
        else:
            raise ValueError(f"Expected a dict or list but got {type(parent)} at key: {key}")

    # Handle the last key or index
    last_key = keys[-1]
    if last_key.isdigit():  # If it's a digit, treat it as a list index
        last_key = int(last_key)

    return (parent, last_key)