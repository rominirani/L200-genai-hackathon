# Base model that defines the required methods for a model implementation

class BaseModel():
    """Base Language Model for generation completions"""
    def generate_content(self, input: str, instruction: str) -> object:
        """Generate completion from the input using instructions"""
        pass

