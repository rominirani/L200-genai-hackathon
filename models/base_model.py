# Base model that defines the required methods for a model implementation


class BaseModel:
    """Base Language Model for generation completions"""

    def __init__(
        self,
        model_name: str = "gemini-1.5-flash",
        generation_config: object = {},
        system_instruction: str = None,
    ):
        """Default constructor arguments"""
        pass

    def generate_content(self, input: str, instruction: str) -> object:
        """Generate completion from the input using instructions"""
        pass
