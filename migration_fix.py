import json
import logging

def extract_translations(old_translation_file: str) -> dict:
    """
    Extracts the orig and trans key-value pairs from the old translation_tkinter.json file.
    
    :param old_translation_file: Path to the old translation_tkinter.json file.
    :return: A dictionary where the key is the orig text and the value is the trans text.
    """
    translations = {}
    
    with open(old_translation_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for json_file_data in data:  # Iterate over each file's data
            texts = json_file_data.get('texts', [])
            for text_info in texts:
                orig_text = text_info.get('orig')
                trans_text = text_info.get('trans')
                if orig_text and trans_text:
                    translations[orig_text] = trans_text  # Store orig as key, trans as value

    logging.info(f"Extracted {len(translations)} translations from {old_translation_file}")
    return translations


def apply_translations_to_new_file(new_translation_file: str, translations: dict) -> None:
    """
    Updates the trans fields in the new translation_tkinter.json file based on matching orig values.
    
    :param new_translation_file: Path to the new translation_tkinter.json file.
    :param translations: A dictionary where the key is the orig text and the value is the trans text.
    """
    with open(new_translation_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    for json_file_data in data:  # Iterate over each file's data in the array
        texts = json_file_data.get('texts', [])
        for text_info in texts:
            orig_text = text_info.get('orig')
            if orig_text in translations:
                text_info['trans'] = translations[orig_text]  # Update trans with the stored value
                logging.info(f"Updated translation for '{orig_text}' to '{translations[orig_text]}'")

    # Save the updated new translation file
    with open(new_translation_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    logging.info(f"Translations applied to {new_translation_file}")


def migrate_translations(old_translation_file: str, new_translation_file: str) -> None:
    """
    Migrates translations from the old translation_tkinter.json to the new one.
    
    :param old_translation_file: Path to the old translation_tkinter.json file.
    :param new_translation_file: Path to the new translation_tkinter.json file.
    """
    # Step 1: Extract all translations from the old file
    translations = extract_translations(old_translation_file)
    
    # Step 2: Apply those translations to the new file
    apply_translations_to_new_file(new_translation_file, translations)


# Example usage:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    old_translation_file = "F:\Games0_0\dev\old_translation_tkinter.json"
    new_translation_file = "F:\Games0_0\dev\\tmp\RJ256202\\translation_tkinter.json"

    migrate_translations(old_translation_file, new_translation_file)
