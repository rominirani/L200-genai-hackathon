# generates completions from models on Vertex AI

from pyexpat import model
from models import BaseModel
import os
import dotenv
import logging

import vertexai
from vertexai.generative_models import GenerativeModel

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

class GeminiVertex(BaseModel):
    """Instantiates the Gemini model from Vertex AI"""

    def __init__(self, 
                 project: str,
                 location: str,
                 model_name: str = "gemini-1.5-flash",
                 generation_config: object = {},
                 system_instruction: str = None):
        """Initialize the model with the given config"""

        logger.info(f"Initializing model {model_name}")
       
        vertexai.init(project=project, location=location)
        self.model = GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        # start chat interface on model
        self.chat_history_writer = []
        self.chat_model = self.model.start_chat(
            history=self.chat_history_writer)

    # override method from BaseModel
    def generate_completion(self, prompt: str) -> object:
        """Override by calling actual model"""
        logger.info("Generating completion")
        
        response = self.chat_model.send_message(prompt)
        self.chat_history_writer.extend([
            {"role": "user", "content": prompt},
            {"role": "model", "content": response.text}
        ])

        return {
            "output": response.text,
            "usage_metadata": {
                "total_tokens": response.usage_metadata.total_token_count,
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count
            }
        }

