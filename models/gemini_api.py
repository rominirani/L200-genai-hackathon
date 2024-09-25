# generates completions from the Gemini 1.5 Flash model

from models import BaseModel
import google.generativeai as genai
import os
import dotenv
import logging

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

class GeminiAPI(BaseModel):
    """Instantiates the Gemini model"""

    def __init__(self, 
                 model_name: str = "gemini-1.5-flash",
                 generation_config: object = {},
                 system_instruction: str = None):

        logger.info(f"Initializing model {model_name}")
        
        """Initialize the model with the given config"""
        genai.configure(api_key=os.getenv("API_KEY"))

        self.model = genai.GenerativeModel(
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
            "response": response.text,
            "usage_metadata": {
                "total_tokens": response.usage_metadata.total_token_count,
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "candidates_tokens": response.usage_metadata.candidates_token_count
            }
        }

