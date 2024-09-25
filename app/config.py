# reads and return the configuration data
import json
import os

from logging import getLogger
logger = getLogger(__name__)


class ConfigReader:
    """Reads and returns the configuration data."""

    # initialise instance attributes
    config_data = {}
    domains = {}
    models = {}


    def __init__(self):
        logger.info('Loading configuration data...')
        self.config_dir = 'config'
        self.config_files = {
            'domains': 'domains.json',
            'models': 'models.json'
        }
        self.config_data = self._read_config()
        self.domains = self.get_domains()
        self.models = self.get_models()


    def _read_config(self):
        config_data = {}
        for key, file_name in self.config_files.items():
            file_path = os.path.join(self.config_dir, file_name)
            logger.info(f'Reading configuration file: {file_path}')
            if not os.path.exists(file_path):
                raise FileNotFoundError(f'Configuration file not found: {file_path}')
            with open(file_path, 'r') as f:
                config_data[key] = json.load(f)
        return config_data
    
    def get_domains(self):
        """Return all the available domains."""
        if not self.domains:
            for domain in self.config_data['domains']:
                self.domains[domain['name']] = domain

        return self.domains
    
    def get_domain(self, name):
        """Returns the config for the given domain."""
        if not self.domains:
            self.get_domains()

        return self.domains[name]

    def get_models(self):
        """Return all the available models."""
        if not self.models:
            for model in self.config_data['models']:
                self.models[model['id']] = model

        return self.models
    
    def get_model(self, id):
        """Returns the config for the given model."""
        if not self.models:
            self.get_models()

        return self.models[id]
    

