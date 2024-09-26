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


    def _read_file(self, file_name):
        """Reads given json config file and returns json object."""
        file_path = os.path.join(self.config_dir, file_name)
        logger.info(f'Reading file: {file_path}')

        # check file exists in OS
        if not os.path.exists(file_path):
            logger.error(f'File not found: {file_path}')
            raise FileNotFoundError(f'File not found: {file_path}')
        with open(file_path, 'r') as f:
            file_json = json.load(f)
        return file_json


    def _read_config(self):
        """Returns the entire configuration data."""
        config_data = {}
        for key, file_name in self.config_files.items():
            config_data[key] = self._read_file(file_name)
  
        logger.debug(f'Configuration data: {config_data}')
        return config_data
    

    def get_domains(self):
        """Return all the available domains."""
        if not self.domains:
            for domain in self.config_data['domains']:
                self.domains[domain['name']] = domain

        logger.debug(f'Domains: {self.domains}')
        return self.domains
    

    def get_domain(self, name):
        """Returns the config for the given domain."""
        if not self.domains:
            self.get_domains()

        logger.debug(f'Domain config: {self.domains[name]}')
        return self.domains[name]

    def get_models(self):
        """Return all the available models."""
        if not self.models:
            for model in self.config_data['models']:
                self.models[model['id']] = model

        logger.debug(f'Models: {self.models}')
        return self.models
    
    def get_model(self, id):
        """Returns the config for the given model."""
        if not self.models:
            self.get_models()

        logger.debug(f'Model config: {self.models[id]}')
        return self.models[id]
    

    def get_config_for_domain(self, domain):
        """Returns the config for the given domain."""
        logger.info(f'Getting config for domain: {domain}')
        config_data = self._read_file(self.get_domain(domain)['config_file'])
        prompts = config_data['prompts']

        # inverse the config so that it is addressable as writer and reviewer
        domain_config = {'writer': {}, 'reviewer': {}}
        domain_config['writer']['prompts'] = prompts.get('writer', {})
        domain_config['reviewer']['prompts'] = prompts.get('reviewer', {})
        domain_config['writer']['model_id'] = config_data['models']['writer']
        domain_config['reviewer']['model_id'] = config_data['models']['reviewer']
        domain_config['iterations'] = config_data.get('iterations', 5)

        logger.debug(f'Domain config: {domain_config}')
        return domain_config

