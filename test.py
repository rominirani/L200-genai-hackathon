from libs import ConfigReader
from models import GeminiAPI
from libs import Generator
import importlib

# Configure the root logger
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)-20s - %(levelname)s - %(message)s')

def test_config():
    config_reader = ConfigReader()
    print(config_reader.get_domains().keys())
    # print(config_reader.get_domain('hackathon'))
    print(config_reader.get_models().keys())
    # print(config_reader.get_model('gemini-15-pro-plain'))
    print(config_reader.get_config_for_domain('hackathon'))


def test_model():
    config_reader = ConfigReader()
    model_config = config_reader.get_model('gemini-15-pro-plain')
    model = GeminiAPI(
        model_name=model_config['model_name'],
        generation_config=model_config['generation_config'],
        system_instruction="Always be unsure and end with a question."
    )
    print(model.generate_completion('How are you?'))


def test_dynamic_model():
    myclass = getattr(importlib.import_module('models'), 'GeminiAPI')
    model = myclass(system_instruction="Always respond saying your bored!")
    print(model.generate_completion('Are you bored?'))


def test_first_iteration():
    cfp = Generator('cfp')
    response = cfp.generate_initial_output(
        prompt="""This talk will be about Firestore. It is a document store.
        It also has vector store support. It has a healthy free tier.
        It has many SDKs and supports GenKit for AI apps.
        """)
    print(response)


def test_full_iteration():
    cfp = Generator('cfp')
    response = cfp.generate_initial_output(
        prompt="""This talk will be about Firestore. It is a document store.
        It also has vector store support. It has a healthy free tier.
        It has many SDKs and supports GenKit for AI apps.
        """)
    response = cfp.generate_iterative_output(response['output'])
    print(response)


# main function
if __name__ == "__main__":
    # test_config()
    # test_model()
    # test_dynamic_model()
    # test_first_iteration()
    test_full_iteration()