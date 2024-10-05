from .util.logging import logging
from .api import send_translation_request
import re
from typing import List, Dict, Any, Tuple
# Function to translate and replace text in JSON files
def translate_texts(texts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Translates the texts and replaces the 'trans' field in the input list of dictionaries.
    
    :param texts: A list of dictionaries, each containing 'id', 'orig', 'trans', and 'ref', and maybe 'in_progress', 'color'.
    """
    
    def remove_psm_command(text: str) -> Tuple[str, str]:
        """
        Removes the PSM_ポップアップ消去/表示 command and the associated numbers, 
        returns the cleaned text and the removed prefix.
        """
        # Remove "PSM_ポップアップ消去" followed by 1 number
        match_remove = re.match(r'^(PSM_ポップアップ消去\s*\d+\s*)', text)
        
        # Remove "PSM_ポップアップ表示" followed by 5 numbers
        match_display = re.match(r'^(PSM_ポップアップ表示\s*(\d+\s*){5})', text)
        
        if match_remove:
            prefix = match_remove.group(0)
            cleaned_text = text[len(prefix):].strip()
        elif match_display:
            prefix = match_display.group(0)
            cleaned_text = text[len(prefix):].strip()
        else:
            prefix = ''
            cleaned_text = text.strip()
        
        return prefix, cleaned_text

    # Preprocess the texts: Remove the PSM commands before sending them for translation
    preprocessed_texts = []
    psm_prefixes = {}  # Store the PSM prefix for each text by its id
    
    for text in texts:
        original_text = text['orig']
        prefix, cleaned_text = remove_psm_command(original_text)
        
        # Always store the PSM prefix by id
        psm_prefixes[text['id']] = prefix
        
        # Only include texts that are not empty after cleaning for translation
        if cleaned_text:
            preprocessed_texts.append({
                'id': text['id'],
                'orig': cleaned_text,
                'ref': text.get('ref')
            })

    # Send translation request for non-empty texts
    translated_texts: List[Tuple[int, str]] = send_translation_request(preprocessed_texts)

    # Map translated text to texts['trans'] based on matching id
    id_to_translation = {id_: text for id_, text in translated_texts}

    # Update the original texts with the translations, re-adding the PSM command
    for text in texts:
        text_id = text.get('id')
        # Re-add the PSM prefix
        prefix = psm_prefixes.get(text_id, '')

        if text_id in id_to_translation:
            # Get the translated text and append the PSM prefix
            translated_text = id_to_translation[text_id]
            text['trans'] = f"{prefix}{translated_text}"
        else:
            # Even if there was no text to translate, add the prefix back
            text['trans'] = prefix
        
        # Clear the 'in_progress' flag after the translation is complete
        text['in_progress'] = False

    # Mark translated texts based on potential errors
    mark_translated_texts(texts)

            
def mark_translated_texts(texts: List[Dict[str, Any]]) -> None:
    """
    Marks the translated text by setting a 'color' field in the text dictionary to green, yellow, or red 
    based on how likely an error is.

    :param texts: A list of dictionaries, each containing 'id', 'orig', 'trans', and 'ref'.
    """
    # Define the criteria for marking the translation
    def mark_text(orig_text: str, trans_text: str) -> str:
        # Check for red flags (code-like elements)
        if (re.search(r'\[.*[\'\"].*\]', trans_text) or check_placeholder_consistency(orig_text, trans_text) or trans_text=='' or check_movement_commands(orig_text)):
            return 'red'
        
        # Check for yellow flags (suspicious elements)
        if ('...' in trans_text or '\\\\' in trans_text or check_length_discrepancy(orig_text, trans_text) or check_mismatched_or_programming_brackets(trans_text)
            or check_numeric_consistency(orig_text, trans_text) or check_special_characters(orig_text) or check_untranslated_text(orig_text, trans_text)):
            return 'yellow'
        
        # If none of the above, mark as green
        return 'green'

    # Iterate over all texts and mark each one
    for text in texts:
        orig_text = text.get('orig', '')
        trans_text = text.get('trans', '')

        if trans_text:  # Only mark texts that have been translated
            color = mark_text(orig_text, trans_text)
            text['color'] = color
            
            
# Functions to check for translation errors
# These functions are used to find common errors in mtl translations and mark them as red, yellow or green

# Function to check untranslated text
def check_untranslated_text(orig_text: str, trans_text: str) -> bool:
    japanese_regex = r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]'
    
    return orig_text == trans_text or bool(re.search(japanese_regex, trans_text))

# Function to check for large discrepancies in text length
def check_length_discrepancy(orig_text: str, trans_text: str) -> bool:
    orig_len = len(orig_text)
    trans_len = len(trans_text)
    # Flag if translated text is too short or too long compared to the original
    return trans_len > orig_len * 4

# Function to check if placeholders like {something} or %var are missing or inconsistent
def check_placeholder_consistency(orig_text: str, trans_text: str) -> bool:
    placeholders = re.findall(r'\{.*?\}|\%\w', orig_text)
    for placeholder in placeholders:
        if placeholder not in trans_text:
            return True  # Flag if a placeholder is missing or changed
    return False

# Function to check if numeric values differ between original and translated text
def check_numeric_consistency(orig_text: str, trans_text: str) -> bool:
    orig_numbers = re.findall(r'\d+', orig_text)
    trans_numbers = re.findall(r'\d+', trans_text)
    return orig_numbers != trans_numbers  # Flag if numbers don't match

# Function to check if special characters are in
def check_special_characters(orig_text: str) -> bool:
    special_chars = ['@', '&', '_']
    return bool([char for char in orig_text if char in special_chars])

# Function to check mismatched brackets and for presence of brackets [] and {}
def check_mismatched_or_programming_brackets(text: str) -> bool:
    stack = []
    brackets = {'(': ')', '[': ']', '{': '}'}
    for char in text:
        if char in brackets.keys():
            if char == '[' or char == '{':
                return True  # Automatically flag for any occurrence of square or curly brackets
            stack.append(brackets[char])
        elif char in brackets.values():
            if not stack or char != stack.pop():
                return True
    return len(stack) != 0  # Return True if there are unclosed round brackets

# New function to check for movement commands like -X, +X, -Y, +Y
def check_movement_commands(orig_text: str) -> bool:
    # Regex to capture movement commands like +X, -X, +Y, -Y (case-insensitive)
    movement_pattern = r'[+-][XY]'
    return bool(re.search(movement_pattern, orig_text, re.IGNORECASE))

