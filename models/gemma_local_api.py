# generates completions from the Gemini 1.5 Flash model

from pyexpat import model
from models import BaseModel
import logging

import ollama

logger = logging.getLogger(__name__)

class GemmaLocalAPI(BaseModel):
    """Instantiates the Gemma2 2b Model running in Ollama locally"""

    def __init__(self, 
                 model_name: str = "gemma2:2b",
                 generation_config: object = {},
                 system_instruction: str = None):
        """Initialize the model with the given config"""

        logger.info(f"Initializing model {model_name}")
        self.model = model_name
        self.format = 'json' \
            if generation_config['response_mime_type'] == 'application/json' else None
        self.chat_history_writer = []
        self.chat_history_writer.append({"role": "system", "content": system_instruction})

    # override method from BaseModel
    def generate_completion(self, prompt: str) -> object:
        """Override by calling actual model"""
        logger.debug(f"Prompt: {prompt}")
        self.chat_history_writer.append({"role": "user", "content": prompt})
        response = ollama.chat(
            model=self.model, 
            format=self.format, 
            messages=self.chat_history_writer)
        logger.debug(f"Response: {response}")
        self.chat_history_writer.append({"role": "assistant", "content": response['message']['content']})

        return {
            "output": response['message']['content'],
            "usage_metadata": {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "candidates_tokens": 0
            }
        }

