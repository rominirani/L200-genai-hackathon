# generates completions from the Gemini 1.5 Flash model

from models import BaseModel
import google.generativeai as genai
import os
import dotenv
import logging

# JSON Schema
from google.ai.generativelanguage_v1beta.types import content

dotenv.load_dotenv(override=True)
logger = logging.getLogger(__name__)


class GeminiAPI(BaseModel):
    """Instantiates the Gemini model"""

    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        generation_config: object = None,
        system_instruction: str = None):
        """Initialize the model with the given config"""

        logger.info(f"Initializing Gemini model {model_name}")
        if not generation_config:
            generation_config = {}

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )

        # start chat interface on model
        self.chat_history_writer = []
        self.chat_model = self.model.start_chat(history=self.chat_history_writer)


    # override method from BaseModel
    def generate_completion(self, prompt: str) -> object:
        """Override by calling actual model"""
        logger.debug(f"Prompt: {prompt}")
        response = self.chat_model.send_message(prompt)
        logger.debug(f"Response: {response}")
        self.chat_history_writer.extend(
            [
                {"role": "user", "content": prompt},
                {"role": "model", "content": response.text},
            ]
        )

        return {
            "output": response.text,
            "usage_metadata": {
                "total_tokens": response.usage_metadata.total_token_count,
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count,
            },
        }
