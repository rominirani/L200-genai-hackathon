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
    metadata = {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "candidates_tokens": 0
            }

    def __init__(self, 
                 domain: str):

        logger.info(f"Initializing generator for domain: {domain}")
        self.config_reader = ConfigReader()
        self.domain_config = self.config_reader.get_config_for_domain(domain)
        logger.debug(f"Domain config: {self.domain_config}")
        self._get_models()


    def _get_models(self):
        """Dynamically instantiates and returns model objects"""

        # create writer model
        logger.info("Creating writer model...")
        model_config = self.config_reader.get_model(
            self.domain_config['writer']['model_id'])
        # writer should return in plaintext / markdown
        model_config["generation_config"]["response_mime_type"] = "text/plain"
        
        # build the model from the config
        logger.debug(f"Model config: {model_config}")
        self.writer = self._build_model(
            model_config["model_class"],
            model_config["model_name"],
            model_config["generation_config"],
            self.domain_config["writer"]["prompts"]["system_prompt"])
        
        # create reviewer model
        logger.info("Creating reviewer model...")
        model_config = self.config_reader.get_model(
            self.domain_config['reviewer']['model_id'])
        # reviewer should return with json and defined schema
        model_config["generation_config"]["response_mime_type"] = "application/json"
        # Set the JSON Output format for reviewer model
        response_schema = {
            "type": "object",
            "properties": {
                "suggestions": {
                    "type": "string",
                    "description": "Provide detailed suggestions for improvement or changes"
                },
                "recommendation": {
                    "type": "string",
                    "enum": ["Approved", "Revise"],
                    "description": "Final recommendation: 'Approved' if no significant changes needed, 'Revise' if changes are required"
                }
            },
            "required": ["suggestions", "recommendation"]
        }
        model_config["generation_config"]["response_schema"] = response_schema

        # build the model from the config
        logger.debug(f"Model config: {model_config}")
        self.reviewer = self._build_model(
            model_config["model_class"],
            model_config["model_name"],
            model_config["generation_config"],
            self.domain_config["reviewer"]["prompts"]["system_prompt"])


    def _build_model(self, 
                     model_class_name: str, 
                     model_name: str, 
                     generation_config: object, 
                     system_instruction: str):
        """create a new model object"""
        model_class = getattr(
            importlib.import_module('models'), model_class_name)
        return model_class(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
    

    def _accumulate_metadata(self, usage_metadata: object):
        """accumulate token counts across all iterations"""
        self.metadata['total_tokens'] += usage_metadata['total_tokens']
        self.metadata['prompt_tokens'] += usage_metadata['prompt_tokens']
        self.metadata['candidates_tokens'] += usage_metadata['candidates_tokens']
        logger.debug(f"Accumulated metadata: {self.metadata}")        


    def generate_initial_output(self, prompt: str):
        """Generate an initial output without iterations"""
        logger.info("Get initial completion from writer")
        logger.debug(f"Prompt: {prompt}")
        review_prompt = \
                self.domain_config['writer']['prompts']['initial_prompt'].replace(
                    _VAR_PROMPT, prompt)
        response = self.writer.generate_completion(review_prompt)
        logger.debug(f"Response: {response}")
        self._accumulate_metadata(response['usage_metadata'])
        return response


    def generate_iterative_output(self, 
                                  initial_output: str, 
                                  num_iterations: int = None):
        """Runs the model iteratively and returns the final output."""

        logger.info('Review initial output')
        logger.debug(f"Initial output: {initial_output}")
        feedback_prompt = \
            self.domain_config['reviewer']['prompts']['initial_prompt'].replace(
                _VAR_PROMPT, initial_output)
        feedback = self.reviewer.generate_completion(feedback_prompt)
        logger.info(f"Recommendation: {json.loads(feedback['output'])['recommendation']}")
        logger.debug(f"Feedback: {feedback}")

        max_iterations = num_iterations or self.domain_config['iterations'] or 3
        self._accumulate_metadata(feedback['usage_metadata'])

        iteration = 0
        response = {}
        logger.info(f'Iterating {max_iterations} times')
        while json.loads(feedback['output'])['recommendation'].lower() == 'revise' \
            and iteration < max_iterations:

            iteration += 1
            logger.info(f"Running iteration {iteration + 1}")

            # iterate output based on feedback
            logger.info('Revise generated output')
            review_prompt = \
                self.domain_config['writer']['prompts']['iterative_prompt'].replace(
                    _VAR_PROMPT, json.loads(feedback['output'])['suggestions'])
            response = self.writer.generate_completion(review_prompt)
            logger.debug(f"Response: {response}")
            self._accumulate_metadata(response['usage_metadata'])

            # review revised output
            logger.info(f'Review generated output')
            feedback_prompt = \
                self.domain_config['reviewer']['prompts']['iterative_prompt'].replace(
                _VAR_PROMPT, response['output'])
            feedback = self.reviewer.generate_completion(feedback_prompt)
            logger.info(f"Recommendation: {json.loads(feedback['output'])['recommendation']}")
            logger.debug(f"Feedback: {feedback}")
            self._accumulate_metadata(feedback['usage_metadata'])


        logger.debug(f"Final output: {response}")
        logger.debug(f"Final metadata: {self.metadata}")
        return {
            'output': response['output'],
            'usage_metadata': self.metadata,
            'iterations': iteration
        }

