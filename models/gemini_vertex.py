# generates completions from models on Vertex AI

from models import BaseModel
import os
import dotenv
import logging

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

class GeminiVertex(BaseModel):
    """Instantiates the Gemini model from Vertex AI"""

    chat_model = {}

    def __init__(self, 
                 model_name: str = "gemini-1.5-flash",
                 generation_config: object = {},
                 system_instruction: str = None):
        """Initialize the model with the given config"""

        logger.info(f"Initializing model {model_name}")
       
        vertexai.init(project=os.getenv("PROJECT_ID"), 
                      location=os.getenv("LOCATION"))

        # Set the JSON Output format for Gemini model
        response_schema = {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "string"
                },
                "recommendation": {
                    "type": "string"
                }
            },
            "required": ["recommendation"]
        }

        # Add another attribute to generation config object
        generation_config['response_schema'] = response_schema
        generation_config['response_mime_type'] = "application/json"

        model = GenerativeModel(
            model_name=model_name,
            generation_config=GenerationConfig(**generation_config),
            system_instruction=system_instruction
        )

        self.chat_model = model.start_chat()


    # override method from BaseModel
    def generate_completion(self, prompt: str) -> object:
        """Override by calling actual model"""
        logger.info("Generating completion")
        
        response = self.chat_model.send_message(prompt)

        return {
            "output": response.text,
            "usage_metadata": {
                "total_tokens": response.usage_metadata.total_token_count,
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count
            }
        }

