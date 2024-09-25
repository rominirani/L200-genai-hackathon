# generates completions from the Gemini 1.5 Flash model

from base_model import BaseModel
import google.generativeai as genai
import os
import dotenv

# load env
dotenv.load_dotenv()

class GeminiFlash15001(BaseModel):
    """Uses Gemini 1.5 Flash model"""

    _MODEL_NAME = "gemini-15-flash-001"

    def __init__(self):
        """Initialize the model"""
        genai.configure(api_key=os.getenv("API_KEY"))
        self.model = genai.get_model(self._MODEL_NAME)

    # override method from BaseModel
    def generate_completion(self, input: str, instruction: str) -> object:
        """Override by calling actual model"""
        return self.model.predict(input, instruction)

