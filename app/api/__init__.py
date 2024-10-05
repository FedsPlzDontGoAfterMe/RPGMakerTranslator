from .GptController import GPTController
from .HfController import HfController
from dotenv import load_dotenv
import os
from typing import List, Dict, Any, Union, Tuple

def send_translation_request(prompt: List[Dict[str, Any]]) -> Union[List[Tuple[int, str]], str]:
    """
    Sends a translation request to the appropriate LLM based on the environment variable 'LLM'.

    :param prompt: A list of dictionaries containing the text to be translated.
                   Each dictionary should have at least an 'id' and 'orig' key.
    :return: A list of tuples (id, translated_text) or an error message if no model is configured.
    """
    load_dotenv()  # Load environment variables
    llm = os.getenv("LLM")  # Get the LLM type from the environment variables
    
    if llm == "GPT":
        gpt_controller = GPTController()  # Instantiate the GPTController
        return gpt_controller.send_translation_request(prompt)  # Send the translation request
    elif llm == "HF":
        hf_controller = HfController()  # Instantiate HfController if needed
        return hf_controller.send_translation_request(prompt)  # Send translation request to HF model
    else:
        return "Model not configured -- please set the LLM environment variable to 'gpt' or 'hf'"