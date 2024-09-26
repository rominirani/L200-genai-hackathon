# generates the completions for a given prompt after iterations
from libs import ConfigReader
import importlib
import json

import logging
logger = logging.getLogger(__name__)

_VAR_PROMPT = "{data}"


class Generator:
    """Executes the primary logic of iteratively generating completions."""

    writer = None
    reviewer = None
    config_reader = None
    domain_config = {}
    iteration = 0

    def __init__(self, 
                 domain: str):

        logger.info(f"Initializing generator for domain: {domain}")
        self.config_reader = ConfigReader()
        self.domain_config = self.config_reader.get_config_for_domain(domain)

        self._get_models(domain)


    def _get_models(self, domain: str):
        """Dynamically instantiates and returns model objects"""

        # create writer model
        logger.info("Creating writer model...")
        model_config = self.config_reader.get_model(
            self.domain_config['writer']['model_id'])
        self.writer = self._build_model(
            model_config["model_class"],
            model_config["model_name"],
            model_config["generation_config"],
            self.domain_config["writer"]["prompts"]["system_prompt"])
        
        # create reader model
        logger.info("Creating reviewer model...")
        model_config = self.config_reader.get_model(
            self.domain_config['reviewer']['model_id'])
        self.reviewer = self._build_model(
            model_config["model_class"],
            model_config["model_name"],
            model_config["generation_config"],
            self.domain_config["reviewer"]["prompts"]["system_prompt"])


    def _build_model(self, 
                     model_class: str, 
                     model_name: str, 
                     generation_config: object, 
                     system_instruction: str):
        """create a new model object"""
        model_class = getattr(
            importlib.import_module('models'), model_class)
        return model_class(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
    

    def generate_initial_output(self, prompt: str):
        """Generate an initial output without iterations"""
        logger.info("Get initial completion from writer")
        response = self.writer.generate_completion(prompt)
        # TODO: Accumalate tokens
        return response


    def generate_iterative_output(self, 
                                  initial_output: str, 
                                  num_iterations: int = 5):
        """Runs the model iteratively and returns the final output."""

        logger.info("Iteratively refine the output")
        feedback_prompt = \
            self.domain_config['reviewer']['prompts']['initial_prompt'].replace(
                _VAR_PROMPT, initial_output)
        feedback = self.reviewer.generate_completion(feedback_prompt)

        while json.loads(feedback['output'])['recommendation'].lower() == 'revise' \
            or self.iteration < num_iterations:
            self.iteration += 1
            logger.info(f"Running iteration {self.iteration}")

            # iterate output based on feedback
            review_prompt = \
                self.domain_config['writer']['prompts']['iterative_prompt'].replace(
                    _VAR_PROMPT, json.loads(feedback['output'])['suggestions'])
            response = self.writer.generate_completion(review_prompt)

            # review revised output
            feedback_prompt = \
                self.domain_config['reviewer']['prompts']['initial_prompt'].replace(
                _VAR_PROMPT, response['output'])
            feedback = self.reviewer.generate_completion(feedback_prompt)

        return {
            'output': response['output'],
            'usage_metadata': response['usage_metadata']
        }

